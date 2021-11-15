#!/usr/bin/env python
# coding: utf-8

from .setup_logging import logging

import re
import pandas
import numpy
import copy

class RasaModel(object):

    def __init__(self,
                 sheets_model,
                 annotate_regex_entities=True,
                 generate_stories=True,
                 include_annotated_examples=True,
                 load_model=True,
                 enable_stdout_logging=True,
                 use_general_style=False):

        self.logger = logging.getLogger(__name__)

        self.logger.propagate = enable_stdout_logging

        if load_model:
            sm = copy.deepcopy(sheets_model)
            self.domain_utterances = self.build_domain_utterances(sm.table_answers,
                                                                  sm.table_strings,
                                                                  sm.table_buttoned_qs)
            self.domain_slots = self.build_domain_slots(sm.table_slots)
            self.domain_entities = self.build_domain_entities(sm.table_entities)
            self.domain_actions = self.build_domain_actions(sm.table_actions)
            self.domain_forms = self.build_domain_forms(sm.table_actions)
            self.domain_intents = self.build_domain_intents(sm.table_nlu)
            self.nlu_training_examples = self.build_nlu_training_examples(
                sm.table_nlu,
                sm.table_nlu_annotations,
                sm.table_entities,
                annotate_regex_entities=annotate_regex_entities,
                include_annotated_examples=include_annotated_examples)

            self.stories = self.build_stories(sm.table_storybuilder,
                                              sm.table_nlu,
                                              generate_stories=generate_stories)


    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k not in ['logger']:
                setattr(result, k, copy.deepcopy(v, memo))
        return result

    def annotate_regex_entities(self, text, pattern_lib):
        """ Annotate training data with entities and synonyms.

            This is a crutch while still on Rasa 1.10.10: once on Rasa 2.x, we
                should make use of the RegexEntityExtractor shipped with Rasa.

            Args:
                text (str): Text to annotate
                pattern_lib (dict): Structure containing the patterns and replacement
                    values to use. It should be of the form:

                    {(entity_name1, entity_synonym1): pattern,
                     (entity_name2, entity_synonym2): pattern}

                    The entity names can be repeated, but each synonym should be unique.
                    This is because one entity may have several patterns mapping
                    to different synonyms:

                    '\b(covid19|corona( ?virus)?)\b' -> disease, covid
                    '\b((virus ?)ebola)\b -> disease, ebola

            Returns:
                str: The input text, potentially modified to include entity annotation.
        """

        def get_overlap_issues(target, candidates):
            """ Get spans overlapping with the target, except the longest one
                (which we want to keep).

                Returns:
                    list: all problematic spans to remove. This includes the target
                        if it is not the longest span.
            """
            o = []
            t_start, t_end = target
            for c in candidates:
                c_start, c_end = c
                # candidate and target straddle
                if (t_start <= c_start < t_end) or t_start <= c_end <= t_end:
                    if c_end - c_start > t_end - t_start:
                        o.append(target)
                    else:
                        o.append(c)
                # candidate is within target
                elif c_start <= t_start and c_end >= t_end:
                    o.append(c)
                # target is within candidate
                elif c_start >= t_start and c_end <= t_end:
                    o.append(target)
                else:
                    continue

            return o

        def repl(s, e_name, e_value):
            return f'[{s}]{{"entity": "{e_name}", "value": "{e_value}"}}'

        def collect_spans(text, pattern_lib):
            """ Find all `patern_lib`'s patterns matches in `text`.

                Returns:
                    dict: where each key is a span tuple (start, end) and each
                        value is a tuple (entity_name, entity_value)
            """
            results = {}
            for key, value in pattern_lib.items():
                for m in re.finditer(pattern=value, string=text):
                    results[m.span()] = key

            return results

        def reduce_spans(spans):
            """ Remove problematic spans."""

            keys = sorted(list(spans.keys()))
            for idx, target in enumerate(keys):
                [spans.pop(x) for x in get_overlap_issues(target, keys[idx+1:])]

            return spans

        def replace_spans(text, spans):
            """Replace captured spans with their annotations."""
            for start, end in sorted(spans.keys(), reverse=True):
                substring = text[start:end]
                e_name = spans[(start, end)][0]
                e_value = spans[(start, end)][1]
                text = f'{text[:start]}{repl(substring, e_name, e_value)}{text[end:]}'

            return text

        spans = collect_spans(text, pattern_lib)
        spans = reduce_spans(spans)
        text = replace_spans(text, spans)

        return text

    def strip_annotation(self, text):
        """ Strip a text from existing annotations (do not use yet, buggy).

            Args:
                text (str): Text for which to strip annotations

            Returns:
                str: The input text, without annotations
        """

        def repl_annotation(m):
            return '{captured}'.format(captured=m.group(1))

        p_annotation = re.compile('\[\\b(.*?)\\b\]\{"entity": "disease", "value": "(covid|ebola)"\}')

        text, n = re.subn(pattern=p_annotation, string=text, repl=repl_annotation)

        return text

    def generate_stories(self, storybuilder, nlu_examples):
        """ Given instructions in a storybuilder, generate stories.

            Rasa stories may be written by hand, but in the case of a FAQ bot
            and very simple interactions, it can make sense to generate them
            automatically.

            TODO:
                - Restrict the use of "xyz_*" patterns to turn 1, or figure out
                  sensible reason why it could be used
                - Write unit tests and check for correctness in story titles,
                  in pattern matching, turns, etc.
                - Validate the storybuilder, warn about errors
                - Write documentation on how to use the storybuilder

            Args:
                storybuilder (pandas.DataFrame): Instructions on how to generate the stories
                nlu_examples (pandas.DataFrame): NLU training examples, used to
                    find unique combinations of intent topic/language

            Returns:
                pandas.DataFrame: Generated stories, one step per row, of the shape:
                    `story_title`,
                    `intent_topic`, `conditions`,
                    `language`,
                    `turn`, `turn_taker`, `step`
        """

        def get_join_keys(row, patterns):
            """ Collecting all matching patterns and picking the longest
                should ensure that it is still possible to generate a story for
                a specific intent, even if it also matches a "xyz_*" pattern.
            """
            matching_patterns = []
            for p_i, p_l in patterns:
                m_pattern = re.match(p_i, row['intent_topic'])
                m_lang = re.match(p_l, row['language'])

                if m_pattern and m_lang:
                    try:
                        p_i_fragment = m_pattern.group(1)
                    except IndexError:
                        p_i_fragment = p_i
                    matching_patterns.append((p_i, p_l, p_i_fragment))

            if matching_patterns:
                # Longest patterns first
                matching_patterns= sorted(matching_patterns,
                                          key=lambda k: len(k[0]),
                                          reverse=True)
                p_i, p_l, p_i_fragment = matching_patterns[0]

                row['intent_pattern'] = p_i
                row['language_pattern'] = p_l
                row['intent_fragment'] = p_i_fragment

            return row

        def get_turn_taker(turn_number):
            x = turn_number % 10
            if x == 0:
                return 'user'
            else:
                return 'bot'

        def format_story_string(row, to_format):
            return row[to_format].format(lang=row['language'],
                                         intent=row['intent_topic'],
                                         fragment=row['intent_fragment'])

        def process_conditions(s):
            """Transform a storybuilder conditions string into a conditions dictionary

                The expected string format is
                    "slot_name1: slot_value1, slot_name2: slot_value2"
                The number of (name,value) pair is not limited.
                Slot names cannot be duplicated.
                Whitespaces are entirely stripped.

                Args:
                    s (str): Conditions string to process
                Returns:
                    dict: Each key is a slot name, each value is a slot value
            """
            if s:
                return {k.strip(): v.strip()
                        for k, v in [y.split(':')
                                     for y in [x.strip()
                                               for x in s.split(',')]
                                    ]
                        }
            else:
                return numpy.nan

        # That should be moved to gsheets
        storybuilder['intent_pattern'] = storybuilder['intent_pattern'].str.replace('*', '(.*)')
        storybuilder['language_pattern'] = storybuilder['language_pattern'].str.replace('*', '(.*)')
        storybuilder['conditions'] = storybuilder['conditions'].apply(lambda k: process_conditions(k))

        patterns = storybuilder[['intent_pattern', 'language_pattern']].to_records(index = False)

        unique_intents = nlu_examples[['intent_topic', 'language']].drop_duplicates()

        spreader_df = unique_intents.apply(lambda row: get_join_keys(row, patterns), axis=1)

        join_indices = ['intent_pattern', 'language_pattern']

        df = (spreader_df.set_index(join_indices)
                         .join(storybuilder.set_index(join_indices),
                               on=['intent_pattern', 'language_pattern'],
                               how='outer')
                         .reset_index()
                         .drop(columns=join_indices)
                         .dropna(subset=['story_title']))

        df['turn_sorter'] = df['turn'] * 10

        df['bot_response_0'] = df.apply(lambda row: '{0}_{1}'.format(row['intent_topic'],
                                                                     row['language']),
                                        axis=1)

        df = df.melt(id_vars=['intent_topic', 'language', 'intent_fragment', 'conditions',
                              'story_title', 'turn', 'turn_sorter'],
                     value_vars=[col for col in df.columns
                                 if col.startswith('bot_response')],
                     var_name='turn_increment',
                     value_name='step')

        df['turn_increment'] = df['turn_increment'].str.extract('([0-9])').astype('int64')
        df['turn_sorter'] = df['turn_sorter'] + df['turn_increment']

        df['step'] = df['step'].replace('^$', numpy.nan, regex=True)
        df = df.dropna(subset=['step'])

        df['step'] = df['step'].str.replace('{', '{{').str.replace('}', '}}')
        df['step'] = df['step'].str.replace('[', '{').str.replace(']', '}')
        df['story_title'] = df['story_title'].str.replace('[', '{').str.replace(']', '}')

        df['step'] = df.apply(lambda row: format_story_string(row, 'step'), axis=1)
        df['story_title'] = df.apply(lambda row: format_story_string(row, 'story_title'), axis=1)

        df['turn_taker'] = df['turn_sorter'].apply(lambda x: get_turn_taker(x))

        # TODO: Sorting turn numbers, and making the series incrase one by one
        # How to do it:
        # l = [0, 1, 5, 9, 10, 3, 100, 7]
        # [idx + 1 for idx, v in enumerate(sorted(l))]


        df = (df.drop(columns=['turn_increment'])
                .sort_values(by=['story_title', 'turn_sorter'])
                .reset_index()
                .reindex(columns=['story_title', 'intent_topic', 'conditions',
                                  'language',
                                  'turn', 'turn_sorter', 'turn_taker', 'step'])
                .dropna(subset=['intent_topic']))

        return df

    def build_domain_utterances(self,
                                table_answers,
                                table_strings,
                                table_buttoned_qs):
        """ Build Rasa domain utterances from tables in the sheets model.

            Args:
                table_answers (pandas.DataFrame): FAQ answers bot utterances
                table_strings (pandas.DataFrame): General chitchat bot utterances
                table_buttoned_qs (pandas.DataFrame): Feedback/survey button questions bot utterances

            Returns:
                pandas.DataFrame: Bot utterances, with shape:
                    `utterance_full_id`, `utterance_topic`,
                    `language`, `channel`, `image`,
                    `utterance_text`, `button_text`, `payload`
        """

        df = (pandas.concat([table_answers,
                             table_strings,
                             table_buttoned_qs],
                            sort=True)
                    .reset_index()
                    .reindex(columns=['utterance_full_id',
                                      'utterance_topic',
                                      'language',
                                      'channel',
                                      'image',
                                      'utterance_text',
                                      'button_text',
                                      'payload']))

        # print(df)

        return df

    def build_domain_slots(self, table_slots):
        """ Build Rasa domain slots from table in the sheets model.

            Currently, the sheets model does not allow complete controls over
            all slot aspects. This function makes sure that the output shape
            includes all the information that may be included in the Rasa
            domain files. Additionally:
                - Slot types "unfeaturized" are changed to "any"
                - Columns "initial_value", "values" (slot type "categorical"),
                    "min_value" and "max_value" (slot type "float") are defaulted to NaN
                - Column "auto_fill" is defaulted to True
                - Column "influence_conversation" is defaulted to True for all
                    slot types other than "unfeaturized" or "any"

            Args:
                table_slots (pandas.DataFrame): Slots used by the bot

            Returns:
                pandas.DataFrame: Slots used by the bot, with shape:
                    `slot_full_id`, `slot_id`, `language`, `slot_type`,
                    `auto_fill`, `influence_conversation`, `initial_value`,
                    `values`, `min_value`, `max_value`
        """

        def split_val(s):
            try:
                return [y for y in [x.strip() for x in s.split(',')] if y]
            except AttributeError:
                return s

        df = table_slots
        # Unfeaturized type is deprecated in v2 and should be replaced by 'any'
        # df['slot_type'].loc[df['slot_type'] == 'unfeaturized'] = 'any'

        df['values'] = df['values'].apply(lambda k: split_val(k))

        df = df.reindex(columns=['slot_full_id', 'slot_id', 'slot_type', 'language',
                                 'auto_fill', 'influence_conversation', 'initial_value',
                                 'values', 'min_value', 'max_value'])

        return df

    def build_domain_entities(self, table_entities):
        """ Build Rasa domain entities from table in the sheets model.

            Zero change for now.

            Args:
                table_entities (pandas.DataFrame): Entities used by the bot

            Returns:
                pandas.DataFrame: Entities used by the bot, with shape:
                    `entity_id`
        """

        return table_entities

    def build_domain_actions(self, table_actions):
        """ Build Rasa domain actions from table in the sheets model.

            Extract actions from the actions and forms table.

            Args:
                table_actions (pandas.DataFrame): Bot actions and forms

            Returns:
                pandas.DataFrame: Bot actions, with shape:
                    `action_full_id`, `action_id`, `language`
        """

        df = (table_actions.loc[table_actions['action_type'] == 'action']
                           .drop(columns=['action_type'])
                           .reset_index(drop=True))
        return df

    def build_domain_forms(self, table_actions):
        """ Build Rasa domain actions from table in the sheets model.

            Extract forms from the actions and forms table.

            Args:
                table_actions (pandas.DataFrame): Bot actions and forms

            Returns:
                pandas.DataFrame: Bot forms, with shape:
                    `form_full_id`, `form_id`, `language`
        """

        df = (table_actions.loc[table_actions['action_type'] == 'form']
                           .drop(columns=['action_type'])
                           .reset_index(drop=True)
                           .rename(columns={'action_full_id' : 'form_full_id',
                                            'action_id': 'form_id'}))
        return df

    def build_domain_intents(self, table_nlu):
        """ Build Rasa domain intents from table in the sheets model.

            We rely on the NLU data to create the intents list, rather than
            a separate intents DataFrame.

            Args:
                table_nlu (pandas.DataFrame): NLU training examples

            Returns:
                pandas.DataFrame: Bot intents, with shape:
                    `intent_full_id`
        """

        df = (table_nlu.dropna(subset=['training_example'])
                       .filter(items=['intent_full_id', 'intent_topic', 'language'])
                       .drop_duplicates()
                       .reset_index(drop=True))

        return df

    def build_nlu_training_examples(self,
                                    table_nlu,
                                    table_annotation=None,
                                    table_entities=None,
                                    annotate_regex_entities=False,
                                    include_annotated_examples=False):
        """ Build Rasa NLU training examples from table in the sheets model.

            TODO:
                - Move regex annotation instructions outside of the code
                - Validate the number of training examples for each intent (minimum 2)

            Args:
                table_nlu (pandas.DataFrame): NLU training examples
                table_annotation (pandas.DataFrame): NLU annotated training examples
                annotate_regex_entities (bool): Whether to automatically annotate
                    training examples where possible
                include_annotated_examples (bool): Whether to include annotated
                    training examples

            Returns:
                pandas.DataFrame: NLU training examples, with shape:
                    `intent_full_id`, `intent_topic`, `language`, `has_entities`, `training_example`, `unannotated_text`
        """

        df = table_nlu

        if include_annotated_examples:
            df2 = table_annotation.filter(items=[
                'intent_full_id', 'intent_topic', 'language', 'training_example'])
            # Remove annotated examples which are already in the training data
            df2 = df2[df2['training_example'].isin(df['training_example']) == False]

            anno_intents = set(df2['intent_topic'].tolist())
            df_intents = set(df['intent_topic'].tolist())
            diff = anno_intents.difference(df_intents)
            if diff:
                self.logger.warning(
                    'The following intents are present in the annotated data, but NOT in the NLU sheet:')
                self.logger.warning(f'{diff}')
                self.logger.warning('Those annotated examples will be removed from the training examples before writing them to file.')
                # Keep only intent_topic which are already in the training data
                df2 = df2[df2['intent_topic'].isin(df['intent_topic'])]

            df = (pandas.concat([df, df2])
                        .dropna(subset=['training_example'])
                        .reset_index(drop=True))


        df.loc[:, 'unannotated_text'] = df['training_example']
        if annotate_regex_entities and table_entities is not None:
            patterns_lib = {}
            for lang_pattern, group in table_entities.groupby(['language_pattern']):
                current_lib = {(row.entity_id, row.synonym) : row.capture_pattern
                               for row in group.itertuples()}
                patterns_lib[lang_pattern] = current_lib
            else:
                for lang in df['language'].unique():
                    patterns_lib[lang] = {
                        ('disease', 'covid'): re.compile(
                            '\\b(corona( ?virus)?|coronavii?rus|coronar|covid(-|=)?(19|10)?|c19|c(-|=)19|virusi ya corona(virus)?)\\b',
                            flags=re.IGNORECASE),
                        ('disease', 'ebola'): re.compile(
                            '\\b(ebola|virus ebola|virusi ya ebola)\\b',
                            flags=re.IGNORECASE)
                    }

            for lang_pattern, current_lib in patterns_lib.items():
                df.loc[df['language'].str.match(lang_pattern), 'training_example'] = (
                    df.apply(lambda row: self.annotate_regex_entities(
                                             row['unannotated_text'],
                                             current_lib),
                             axis=1)
                )

        df.loc[:, 'has_entities'] = df['training_example'] != df['unannotated_text']

        df = (df.reindex(columns=['intent_full_id', 'intent_topic', 'language', 'has_entities', 'training_example', 'unannotated_text'])
                .reset_index(drop=True))

        return df

    def build_stories(self, table_storybuilder, table_nlu, generate_stories):
        """ Build Rasa stories from table in the sheets model.

            Why not just rename `generate_stories` as `build_stories`, since
            `build_stories` doesn't really do anything new?
            I want to keep the wrapper to potentially:
                - Allow for non-generated stories
                - Override when experimenting

            Args:
                table_storybuilder (pandas.DataFrame): Instructions on how to generate the stories
                table_nlu (pandas.DataFrame): NLU training examples
                generate_stories (bool): Whether to generate stories

            Returns:
                pandas.DataFrame: Generated stories, one step per row, of the shape:
                    `story_title`, `intent_topic`, `language`,
                    `turn`, `turn_taker`, `step`
        """


        if generate_stories:
            return self.generate_stories(table_storybuilder, table_nlu)
