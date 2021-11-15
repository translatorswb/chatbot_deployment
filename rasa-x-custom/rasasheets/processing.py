#!/usr/bin/env python
# coding: utf-8

from .setup_logging import logging

import re
import pandas
import numpy
import copy

class Processor(object):
    """Transform a SheetsModel or a RasaModel object as requested.

    All methods take either a SheetsModel or RasaModel object as input and
    return the same object updated, or a copy if requested.
    The goal is to make it easy to filter or add data to the model: removing
    intents from a model does not mean only to edit the training data, but
    also to make sure that no reference to these intents is present elsewhere

    """

    logger = logging.getLogger(__name__)

    @classmethod
    def _check_filtering_params(cls, to_keep, to_remove):
        """Check if filtering parameters are correctly filled.

        Args:
            to_keep (list) -- Values to keep
            to_remove (list) -- Values to remove

        Returns:
            tuple (bool, list): The boolean is to know whether to flip the mask
                when filtering in pandas:
                >>> [True == x for x in [True, False, True]]
                [True, False, True]
                >>> [False == x for x in [True, False, True]]
                [False, True, False]
                The list is the parameter to use in pandas to build the mask
        """

        try:
            assert to_keep or to_remove
        except AssertionError:
            logger.warning(
                '`to_keep` and `to_remove` are empty, no filtering will take place')
            return sheets_model

        try:
            assert type(to_keep) is list
            assert type(to_remove) is list
            for x in to_keep + to_remove:
                assert type(x) is str

        except AssertionError:
            logger.error('`to_keep` and `to_remove` (use one only) need to be lists of strings, or empty')
            raise

        try:
            assert not (to_keep and to_remove)
        except AssertionError:
            logger.error('Use either `to_keep` or `to_remove`, not both')
            raise

        if to_keep:
            return (True, to_keep)
        elif to_remove:
            return (False, to_remove)

    @classmethod
    def _copy_or_not(cls, model, inplace):
        if inplace:
            m = model
        else:
            m = copy.deepcopy(model)
        return m

    @classmethod
    def filter_intent_topics_sm(cls, sheets_model, to_keep=[], to_remove=[], inplace=True):

        id_mask, sel = cls._check_filtering_params(to_keep, to_remove)
        sm = cls._copy_or_not(sheets_model, inplace)

        sm.table_nlu = sm.table_nlu[sm.table_nlu['intent_topic'].isin(sel) == id_mask]
        sm.table_intents = sm.table_intents[sm.table_intents['intent_topic'].isin(sel) == id_mask]
        sm.table_answers = sm.table_answers[sm.table_answers['intent_topic'].isin(sel) == id_mask]

        return sm

    @classmethod
    def filter_intent_sm(cls, sheets_model, to_keep=[], to_remove=[], inplace=True):

        id_mask, sel = cls._check_filtering_params(to_keep, to_remove)
        sm = cls._copy_or_not(sheets_model, inplace)

        utter_sel = ['utter_{x}'.format(x=x) for x in sel]

        sm.table_nlu = sm.table_nlu[sm.table_nlu['full_id'].isin(sel) == id_mask]
        sm.table_answers = sm.table_answers[sm.table_answers['intent_full_id'].isin(utter_sel) == id_mask]

        return sm

    @classmethod
    def filter_languages_sm(cls, sheets_model, to_keep=[], to_remove=[], inplace=True):

        id_mask, sel = cls._check_filtering_params(to_keep, to_remove)
        sm = cls._copy_or_not(sheets_model, inplace)

        sel = [x.lower() for x in sel]

        sm.table_nlu = (
            sm.table_nlu[sm.table_nlu['language'].isin(sel) == id_mask])
        sm.table_actions = (
            sm.table_actions[sm.table_actions['language'].isin(sel) == id_mask])
        sm.table_buttoned_qs = (
            sm.table_buttoned_qs[sm.table_buttoned_qs['language'].isin(sel) == id_mask])
        sm.table_answers = (
            sm.table_answers[sm.table_answers['language'].isin(sel) == id_mask])
        sm.table_strings = (
            sm.table_strings[sm.table_strings['language'].isin(sel) == id_mask])

        return sm

    @classmethod
    def filter_intent_topics_rsm(cls, rasa_model, to_keep=[], to_remove=[], inplace=True):
        """ Filter data stored in a Rasa Model by intent topic.

            Use either `to_keep` OR `to_remove`, not both.

            Args:
                rasa_model (rasasheets.model.RasaModel): Model to filter
                to_keep (list of str): Intent topics to keep
                to_remove (list of str): Intent topics to remove
                inplace (bool): Wheter to modify in place

            Returns:
                rasasheets.model.RasaModel: The filtered model
        """

        id_mask, sel = cls._check_filtering_params(to_keep, to_remove)
        rsm = cls._copy_or_not(rasa_model, inplace)

        rsm.nlu_training_examples = rsm.nlu_training_examples[rsm.nlu_training_examples['intent_topic'].isin(sel) == id_mask]

        rsm.domain_intents = rsm.domain_intents[rsm.domain_intents['intent_topic'].isin(sel) == id_mask]

        # We grab the story title when 'step' matches the selection: it becomes
        # the new `to_keep` or new `to_remove`
        story_sel = rsm.stories[rsm.stories['intent_topic'].isin(sel)]['story_title'].unique()

        # print('\n\nStory title selection')
        # print(story_sel)

        # Filter as usual using the id_mask
        rsm.stories = rsm.stories[rsm.stories['story_title'].isin(story_sel) == id_mask]

        # print('\n\nOutput stories:')
        # print(rsm.stories)

        return rsm

    @classmethod
    def filter_intent_rsm(cls, rasa_model, to_keep=[], to_remove=[], inplace=True):
        """ Filter data stored in a Rasa Model by intent.

            Use either `to_keep` OR `to_remove`, not both.

            Args:
                rasa_model (rasasheets.model.RasaModel): Model to filter
                to_keep (list of str): Intents to keep
                to_remove (list of str): Intents to remove
                inplace (bool): Wheter to modify in place

            Returns:
                rasasheets.model.RasaModel: The filtered model
        """

        id_mask, sel = cls._check_filtering_params(to_keep, to_remove)
        rsm = cls._copy_or_not(rasa_model, inplace)

        rsm.nlu_training_examples = rsm.nlu_training_examples[rsm.nlu_training_examples['intent_full_id'].isin(sel) == id_mask]

        rsm.domain_intents = rsm.domain_intents[rsm.domain_intents['intent_full_id'].isin(sel) == id_mask]

        # We grab the story title when 'step' matches the selection: it becomes
        # the new `to_keep` or new `to_remove`
        story_sel = rsm.stories[rsm.stories['step'].isin(sel)]['story_title'].unique()

        # print('\n\nStory title selection')
        # print(story_sel)

        # Filter as usual using the id_mask
        rsm.stories = rsm.stories[rsm.stories['story_title'].isin(story_sel) == id_mask]

        # print('\n\nOutput stories:')
        # print(rsm.stories)

        return rsm


    @classmethod
    def filter_languages_rsm(cls,
                             rasa_model,
                             to_keep=[],
                             to_remove=[],
                             keep_multilingual=True,
                             simplify_monolingual_full_ids=True,
                             inplace=True):

        """ Filter data stored in a Rasa Model by language.

            Use either `to_keep` OR `to_remove`, not both.

            Args:
                rasa_model (rasasheets.model.RasaModel): Model to filter
                to_keep (list of str): Languages to keep
                to_remove (list of str): Languages to remove
                keep_multilingual (bool): Whether to keep data common to all
                    languages (example, `action_out_of_scope`)
                inplace (bool): Wheter to modify in place

            Returns:
                rasasheets.model.RasaModel: The filtered model
        """

        def strip_full_id_language_tag(full_id, pattern):
            return re.sub(string=full_id, pattern=pattern, repl='')

        id_mask, sel = cls._check_filtering_params(to_keep, to_remove)
        rsm = cls._copy_or_not(rasa_model, inplace)

        sel = [x.lower() for x in sel]
        simplify_monolingual_full_ids = simplify_monolingual_full_ids and len(sel) == 1

        # Remember id_mask == True means 'to_keep', and id_mask == False means 'to_remove'
        #  Explicitely INclude NaN            Explicitely EXclude NaN
        if (id_mask and keep_multilingual) or (not id_mask and not keep_multilingual):
            sel.append(numpy.nan)

        rsm.nlu_training_examples = rsm.nlu_training_examples[rsm.nlu_training_examples['language'].isin(sel) == id_mask]

        rsm.stories = rsm.stories[rsm.stories['language'].isin(sel) == id_mask]

        rsm.domain_utterances = rsm.domain_utterances[rsm.domain_utterances['language'].isin(sel) == id_mask]
        rsm.domain_intents = rsm.domain_intents[rsm.domain_intents['language'].isin(sel) == id_mask]
        rsm.domain_actions = rsm.domain_actions[rsm.domain_actions['language'].isin(sel) == id_mask]
        rsm.domain_forms = rsm.domain_forms[rsm.domain_forms['language'].isin(sel) == id_mask]
        rsm.domain_slots = rsm.domain_slots[rsm.domain_slots['language'].isin(sel) == id_mask]

        if simplify_monolingual_full_ids:
            rsm = cls.simplify_full_ids_for_monolingual_rsm(rsm, sel[0], inplace=inplace)

        return rsm

    @classmethod
    def simplify_full_ids_for_monolingual_rsm(cls, rasa_model, language, inplace=True):
        """Strip the language tags from a RasaModel object's full_ids of a RasaModel."""

        def strip_full_id_language_tag(full_id, pattern):
            return re.sub(string=full_id, pattern=pattern, repl='')

        rsm = cls._copy_or_not(rasa_model, inplace)
        language = language.lower()

        p = re.compile(f'_{language}$')

        rsm.nlu_training_examples['intent_full_id'] = rsm.nlu_training_examples['intent_full_id'].apply(lambda k:strip_full_id_language_tag(k, p))
        rsm.stories['story_title'] = rsm.stories['story_title'].apply(lambda k:strip_full_id_language_tag(k, p))
        rsm.stories['step'] = rsm.stories['step'].apply(lambda k:strip_full_id_language_tag(k, p))

        rsm.domain_utterances['utterance_full_id'] = rsm.domain_utterances['utterance_full_id'].apply(lambda k:strip_full_id_language_tag(k, p))
        rsm.domain_intents['intent_full_id'] = rsm.domain_intents['intent_full_id'].apply(lambda k:strip_full_id_language_tag(k, p))
        rsm.domain_actions['action_full_id'] = rsm.domain_actions['action_full_id'].apply(lambda k:strip_full_id_language_tag(k, p))
        rsm.domain_forms['form_full_id'] = rsm.domain_forms['form_full_id'].apply(lambda k:strip_full_id_language_tag(k, p))
        rsm.domain_slots['slot_full_id'] = rsm.domain_slots['slot_full_id'].apply(lambda k:strip_full_id_language_tag(k, p))

        return rsm

    @classmethod
    def merge_intent_topics_rsm(cls, rasa_model, to_merge, inplace=True):
        """ Merge intent topic data stored in a Rasa Model.

            Args:
                rasa_model (rasasheets.model.RasaModel): Model to filter
                target_topic (str): `to_merge` intent topic will be renamed as `target_topic`
                to_merge (list of str): Intent topics to merge under the same
                    name as the first intent in the list
                inplace (bool): Wheter to modify in place

            Returns:
                rasasheets.model.RasaModel: The merged model
        """

        rsm = cls._copy_or_not(rasa_model, inplace)

        # First element of `to_merge` becomes the target topic
        target_topic, *to_merge = to_merge

        targets = rsm.nlu_training_examples['intent_topic'].isin(to_merge)
        rsm.nlu_training_examples.loc[targets, 'intent_topic'] = target_topic
        rsm.nlu_training_examples.loc[targets, 'intent_full_id'] = rsm.nlu_training_examples['intent_topic'] + '_' + rsm.nlu_training_examples['language']

        targets = rsm.domain_intents['intent_topic'].isin(to_merge)
        rsm.domain_intents.loc[targets, 'intent_topic'] = target_topic
        rsm.domain_intents.loc[targets, 'intent_full_id'] = rsm.domain_intents['intent_topic'] + '_' + rsm.domain_intents['language']
        rsm.domain_intents = rsm.domain_intents.drop_duplicates().reset_index()

        target_topic_already_exists = target_topic in rsm.stories['intent_topic'].tolist()

        if not target_topic_already_exists:
            # We change the first element of the `to_merge` structure to the
            # target topic, and we'll then just drop the rest
            topic_to_merge, *to_merge = to_merge

            rsm.stories.loc[rsm.stories['intent_topic'] == topic_to_merge, 'intent_topic'] = target_topic

            # Couldn't figure out a more elegant way of doing this
            for lang in rsm.stories.language.unique():
                rsm.stories.loc[rsm.stories['step'] == f'{topic_to_merge}_{lang}', 'step'] = f'{target_topic}_{lang}'
                rsm.stories.loc[rsm.stories['story_title'] == f'{topic_to_merge}_{lang}', 'story_title'] = f'{target_topic}_{lang}'

        # Since the target topic already exists (we made sure of that), we just
        # want to remove the stories mentionning the intent topics in `to_merge`
        story_sel = rsm.stories[rsm.stories['intent_topic'].isin(to_merge)]['story_title'].unique()
        rsm.stories = rsm.stories[rsm.stories['story_title'].isin(story_sel) == False]

        return rsm
