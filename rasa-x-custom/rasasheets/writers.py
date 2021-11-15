#!/usr/bin/env python
# coding: utf-8

from .setup_logging import logging

import sys
import os
import ruamel.yaml
import pandas
import numpy
import collections

# ===== Output files =====
# DOMAIN_YML_FILE = 'domain.yml'
# STORIES_MD_FILE = 'stories.md'
# NLU_MD_FILE = 'nlu.md'
# TESTS_MD_FILE = 'conversation_tests.md'

# ===== Other constants =====
# SESSION_EXPIRATION_TIME = '60'
# CARRY_OVER_SLOTS_TO_NEW_SESSION = 'true'
# IS_MULTILINGUAL = len(LANGUAGES) > 1

class MarkdownWriter(object):


    @classmethod
    def format_md_content(cls,
                          content,
                          content_prefix='', content_sep='',
                          start_symbol='',
                          indent_level=0, indent_amount=2):

        formatted_content = '{content_prefix}{content_sep}{content}'.format(content_prefix=content_prefix,
                                                                            content_sep=content_sep,
                                                                            content=content)

        return '{indent}{start_symbol}{formatted_content}\n'.format(indent=' ' * indent_level * indent_amount,
                                                                    start_symbol=start_symbol,
                                                                    formatted_content=formatted_content)


    @classmethod
    def format_NLU_title(cls, content, content_type):
        return cls.format_md_content(start_symbol='## ',
                                     content_prefix=content_type,
                                     content_sep=': ',
                                     content=content)

    @classmethod
    def format_NLU_training_example(cls, content):
        return cls.format_md_content(start_symbol='- ',
                                     content=content,
                                     indent_level=1)

    @classmethod
    def format_story_title(cls, content):
        return cls.format_md_content(start_symbol='## ',
                                     content=content)

    @classmethod
    def format_story_user_utterance(cls, content, conditions=None):
        if conditions:
            data = ', '.join([f'"{k}": "{v}"' for k, v in conditions.items()])
            content = f'{content}{{{data}}}'

        return cls.format_md_content(start_symbol='* ',
                                     content=content,
                                     indent_level=1)

    @classmethod
    def format_story_bot_action(cls, content):
        return cls.format_md_content(start_symbol='- ',
                                     content=content,
                                     indent_level=2)

class NLUDataWriter(MarkdownWriter):

    logger = logging.getLogger(__name__)

    @classmethod
    def format_section(cls, element_id, element_type, training_examples):
        return [cls.format_NLU_title(element_id, element_type)] + [cls.format_NLU_training_example(x) for x in training_examples]

    @classmethod
    def format_intents_section(cls, intent_id, training_examples):
        return cls.format_section(intent_id, 'intent', training_examples)

    @classmethod
    def format_synonyms_section(cls, synonym_value, training_examples):
        return cls.format_section(intent_id, 'synonym', training_examples)


class StoriesWriter(MarkdownWriter):

    logger = logging.getLogger(__name__)

    @classmethod
    def format_story_step(cls, user_utterance, bot_actions, conditions=None):
        """Format an entire step of a story.

        Format a story step, that is one user utterance, and one or more bot actions.
        Once formatted and written, the Markdown for a story step looks like::

            * share_with_your_friends_swc
              - utter_share_with_your_friends_swc
              - utter_anything_else_swc

        That's one user utterance and two bot actions

        Args:
            user_utterance (str): The user utterance triggering the story step.
            bot_actions (list of str): The bot actions executed in response.

        Returns:
            list of str: A list of formatted Markdown lines
        """
        if not isinstance(conditions, dict):
            conditions = None

        formatted_user_utterance = cls.format_story_user_utterance(user_utterance, conditions)

        return [formatted_user_utterance] + [cls.format_story_bot_action(x) for x in bot_actions]

    @classmethod
    def format_story(cls, story_id, formatted_story_steps):
        full_story = [cls.format_story_title(story_id)]
        for story_step in formatted_story_steps:
            full_story.extend(story_step)
        return full_story

class RasaWriter(NLUDataWriter, StoriesWriter):

    logger = logging.getLogger(__name__)

    @classmethod
    def write_rasa_files(cls,
                         rasa_model,
                         output_directory_path='.',
                         output_data_dirname='data',
                         domain_filename='domain.yml',
                         nlu_filename='nlu.md',
                         stories_filename='stories.md',
                         session_expiration_time=60,
                         carry_over_slots_to_new_session=True,
                         version='1.0'):

        output_directory_path = os.path.abspath(output_directory_path)
        data_dirpath = os.path.join(output_directory_path,
                                    output_data_dirname)
        os.makedirs(data_dirpath,
                    exist_ok=True)

        domain_filepath = os.path.join(output_directory_path,
                                       domain_filename)
        nlu_filepath = os.path.join(data_dirpath,
                                    nlu_filename)
        stories_filepath = os.path.join(data_dirpath,
                                        stories_filename)

        cls.write_domain(rasa_model,
                         domain_filepath,
                         include_responses=True,
                         session_expiration_time=session_expiration_time,
                         carry_over_slots_to_new_session=carry_over_slots_to_new_session,
                         version=version)

        cls.write_nlu(rasa_model,
                      nlu_filepath,
                      version=version)

        cls.write_stories(rasa_model, stories_filepath)

        return True

    @classmethod
    def write_domain(cls,
                     rasa_model,
                     filename,
                     include_responses=True,
                     session_expiration_time=60,
                     carry_over_slots_to_new_session=True,
                     version='1.0'):
        o = {'version'       : version,
             'intents'       : cls.convert_domain_intents(rasa_model.domain_intents),
             'forms'         : cls.convert_domain_forms(rasa_model.domain_forms),
             'actions'       : cls.convert_domain_actions(rasa_model.domain_actions),
             'entities'      : cls.convert_domain_entities(rasa_model.domain_entities),
             'slots'         : cls.convert_domain_slots(rasa_model.domain_slots,
                                                        version=version),
             'session_config': cls.make_session_config(session_expiration_time,
                                                       carry_over_slots_to_new_session)
        }
        if include_responses:
            o['responses'] = cls.convert_domain_utterances(rasa_model.domain_utterances)

        o = {k: v for k, v in o.items() if v}

        cls.logger.info(f'Writing domain data to {filename}...')
        with open(filename, 'w') as f:
            ruamel.yaml.dump(o,
                             f,
                             allow_unicode=True,
                             default_flow_style=False,
                             default_style=None,
                             line_break=True,
                             indent=4,
                             block_seq_indent=2,
                             width=140)
        return True

    @classmethod
    def write_responses(cls,
                        rasa_model,
                        filename,
                        version='1.0'):

        if isinstance(rasa_model, pandas.DataFrame):
            df = rasa_model
        else:
            df = rasa_model.domain_utterances

        o = {'version': version,
             'responses': cls.convert_domain_utterances(df)}

        cls.logger.info(f'Writing responses data to {filename}...')
        with open(filename, 'w') as f:
            ruamel.yaml.dump(o,
                             f,
                             allow_unicode=True,
                             default_flow_style=False,
                             default_style=None,
                             line_break=True,
                             indent=4,
                             block_seq_indent=2,
                             width=140)
        return True


    @classmethod
    def write_stories(cls, rasa_model, filename):
        if isinstance(rasa_model, pandas.DataFrame):
            df = rasa_model
        else:
            df = rasa_model.stories

        cls.logger.info(f'Writing stories data to {filename}...')
        with open(filename, 'w') as f:
            for line in cls.convert_stories(df):
                f.write(line)
        return True

    @classmethod
    def write_nlu(cls, rasa_model, filename, version='1.0'):
        version = int(float(version))

        if isinstance(rasa_model, pandas.DataFrame):
            df = rasa_model
        else:
            df = rasa_model.nlu_training_examples

        cls.logger.info(f'Writing nlu data to {filename}...')
        with open(filename, 'w') as f:
            if version == 1 :
                for line in cls.convert_nlu_training_examples(df):
                    f.write(line)
            elif version == 2 :
                o = {'nlu': [], 'version': '2.0'}
                for (lang, intent_id), group in df.groupby(['language', 'intent_full_id']):
                    o['nlu'].append({
                        'intent': intent_id,
                        'examples': group['training_example'].to_list()
                    })
                ruamel.yaml.dump(o,
                                 f,
                                 allow_unicode=True,
                                 default_flow_style=False,
                                 default_style=None,
                                 line_break=True,
                                 indent=4,
                                 block_seq_indent=2,
                                 width=140)

        return True

    @classmethod
    def make_session_config(cls, session_expiration_time, carry_over_slots_to_new_session):
        return {'session_expiration_time' : session_expiration_time,
                'carry_over_slots_to_new_session' : carry_over_slots_to_new_session}


    @classmethod
    def convert_nlu_training_examples(cls, table_nlu):
        grouped_nlu = table_nlu.groupby(['language', 'intent_full_id'], sort=False)
        formatted = []

        previous = None
        for name, group in grouped_nlu:
            if name[0] != previous:
                formatted.extend([
                    '\n',
                    '<!-- {lang} Training examples -->'.format(lang=name[0].upper()),
                    '\n'])
                previous = name[0]

            formatted.extend(cls.format_intents_section(name[1], group['training_example']))
            formatted.append('\n')

        return formatted

    @classmethod
    def convert_stories(cls, table_stories):
        grouped_stories = table_stories.groupby(['language', 'story_title'], sort=True)
        formatted = []

        previous = None
        for name, group in grouped_stories:
            if name[0] != previous:
                formatted.extend([
                    '\n',
                    '<!-- {lang} Stories -->'.format(lang=name[0].upper()),
                    '\n'])
                previous = name[0]

            # Format each step
            current = []
            for step_turn, step_group in group.groupby('turn', sort=False):
                user_step = step_group[step_group['turn_taker'] == 'user']['step'].to_list()[0]
                slot_conditions = step_group[step_group['turn_taker'] == 'user']['conditions'].to_list()[0]
                bot_steps = step_group[step_group['turn_taker'] == 'bot']['step'].to_list()
                current.append(cls.format_story_step(user_step, bot_steps, slot_conditions))

            # Assemble and add to list
            formatted.extend(cls.format_story(name[1], current))
            formatted.append('\n')

        return formatted


    @classmethod
    def convert_domain_utterances(cls, table_utterances):

        def get_buttons(group):
            rec = (group[['button_text', 'payload']].dropna()
                                                    .to_records(index=False))
            return [{'title' : x[0], 'payload': x[1]}
                    for x in rec]

        # Pandas >= 1.0 allows a dropna=False argument on the groupby, which would
        # remove the need for the ugly fillna on the "channel" column
        table_utterances['channel'] = table_utterances['channel'].fillna('')
        grouped_utterances = table_utterances.groupby(['language', 'utterance_full_id',
                                                       'utterance_text', 'channel'],
                                                      sort=False)
        formatted = collections.defaultdict(list)

        for (lang, utt_id, utt_text, channel), group in grouped_utterances:
            buttons = get_buttons(group)

            try:
                utt = {'text': (group['utterance_text'].to_list())[0]}
            except:
                cls.logger.warning('Problem with utterance for {name}'.format(name=utt_id))

            key_buttons = 'buttons'
            key_image = 'image'

            channel = group['channel'].to_list()[0]
            if channel in ['facebook', 'telegram', 'twilio', 'slack']:
                utt['channel'] = channel

            if channel == 'facebook':
                key_buttons = 'quick_replies'

            image = group['image'].to_list()[0]
            if isinstance(image, str):
                utt[key_image] = image

            if buttons:
                utt[key_buttons] = buttons

            formatted[utt_id].append(utt)

        return dict(formatted)


    @classmethod
    def convert_domain_slots(cls, table_slots, version='1.0'):

        def get_slot(row, version):
            o = {'type' : row['slot_type']}

            if not row['auto_fill']:
                o['auto_fill'] = row['auto_fill']

            if version == 1:
                o['type'] = 'unfeaturized' if o['type'] == 'any' else o['type']
            elif version > 1:
                o['type'] = 'any' if o['type'] == 'unfeaturized' else o['type']

                if row['slot_type'] != 'any' and not row['influence_conversation']:
                    o['influence_conversation'] = row['influence_conversation']

            if not numpy.isnan(row['initial_value']):
                o['initial_value'] = row['initial_value']

            if row['slot_type'] == 'categorical':# and not numpy.isnan(row['values']):
                # o['values'] = row['values'].replace(' ', '').split(',')
                o['values'] = row['values']

            if row['slot_type'] == 'float':
                if not numpy.isnan(row['min_value']):
                    o['min_value'] = float(row['min_value'])
                if not numpy.isnan(row['max_value']):
                    o['max_value'] = float(row['max_value'])

            return o

        version = int(float(version))
        formatted = table_slots.sort_values(by=['language', 'slot_full_id'])
        formatted['val'] = formatted.apply(lambda row: get_slot(row, version),
                                           axis=1)
        formatted = (formatted.set_index('slot_full_id')
                              .to_dict('dict'))['val']

        return formatted

    @classmethod
    def convert_domain_entities(cls, table_entities):
        if table_entities is None:
            return []
        return table_entities['entity_id'].drop_duplicates().to_list()

    @classmethod
    def convert_domain_actions(cls, table_actions):
        return (table_actions.sort_values(['language', 'action_full_id'])
                             .action_full_id
                             .to_list())

    @classmethod
    def convert_domain_forms(cls, table_forms):
        return (table_forms.sort_values(['language', 'form_full_id'])
                           .form_full_id
                           .to_list())

    @classmethod
    def convert_domain_intents(cls, table_intents):
        return (table_intents.sort_values(['language', 'intent_full_id'])
                             .intent_full_id
                             .to_list())
