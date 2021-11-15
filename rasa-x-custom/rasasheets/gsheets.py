#!/usr/bin/env python
# coding: utf-8

from .setup_logging import logging
from .constants import *

import gspread
import re
import ruamel.yaml
import pandas
import numpy
import copy

class SheetsModel(object):

    def __init__(self,
                 spreadsheet_links=None,
                 requested_languages=None,
                 load_model=True,
                 enable_stdout_logging=True,
                 service_account_override=None):
        self.logger = logging.getLogger(__name__)

        self.logger.propagate = enable_stdout_logging
        self.gc = self.setup_gspread(service_account_override)

        if load_model:
            assert spreadsheet_links is not None
            assert isinstance(spreadsheet_links, list)

            self.sheet_names = SHEET_NAMES
            self.worksheets = self.find_worksheets(spreadsheet_links)

            self.load_all_records(self.worksheets, self.sheet_names)

            self.language_codes = self.get_language_codes(self.records_nlu, requested_languages)
            self.process_all_records()

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
            if k not in ['gc', 'logger', 'worksheets']:
                try:
                    setattr(result, k, copy.deepcopy(v, memo))
                except:
                    print(f'Deep copy fails on attribute `{k}`')
                    raise
        return result

    def setup_gspread(self, service_account_override):
        try:
            if service_account_override:
                return gspread.service_account(filename=service_account_override)
            else:
                return gspread.service_account()
        except:
            self.logger.error('Couldn\'t create a gspread client.')
            self.logger.warning('You need a "service_account.json" token for gspread in order to access the model spreadsheets.')
            self.logger.warning('Ask Étienne, Faizan, or someone else in the dev team.')
            raise

    def get_language_codes(self, records_nlu, requested_languages=None):

        detected_languages = {key.upper() for key in records_nlu[0].keys() if key in LANGUAGES}
        if requested_languages:
            requested_languages = {x.upper() for x in requested_languages}
            languages_not_in_sheets = requested_languages - detected_languages
            if languages_not_in_sheets:
                self.logger.error('Languages requested couldn\'t be found in the sheets model')
                self.logger.error('{languages_not_in_sheets}'.format(languages_not_in_sheets=languages_not_in_sheets))
                raise ValueError
            else:
                language_codes = requested_languages

        else:
            self.logger.warning('No specific language codes given when creating the Sheets Model.')
            self.logger.warning('Defaulting to languages detected in the NLU sheet')
            language_codes = detected_languages

        self.logger.info('I will load the following languages: {langs}'.format(langs=language_codes))
        return list(language_codes)

    def make_id(self, element_id, sep='_', prefix=None, language_code=None):
        """General ID maker.

        `make_id` strips all whitespace and newlines from `element_id`.

        Args:
            element_id (str): The name of the element.
                Examples: 'covid_symptoms', 'affirm'
            sep (str): The separator character to use. Default to '_'
            prefix (str or None): A prefix for the `element_id`
                Examples: 'utter', 'ask', 'action'
            language_code (str or NONE): A 3-letters language code (which gets lowered) to append to the `element_id`
                Examples: 'lin', 'swc', 'fra', 'LIN', 'SWC', 'FRA'

        Returns:
            str: A constructed id.

        Examples:
            >>> make_id(element_id='answer_covid_symptoms', prefix='utter', language_code='lin')
            "utter_answer_covid_symptoms_lin"
        """
        try:
            assert element_id
            assert isinstance(element_id, str)
            assert isinstance(language_code, str) or language_code is None
        except AssertionError:
            self.logger.warning(f'Missing ID ({element_id}) or incorrect language code ({language_code})')
            return numpy.nan

        # No whitespace or newlines allowed
        element_id = ''.join(element_id.strip())
        if not element_id:
            self.logger.error(f'Corrupted id: {element_id} {prefix} {language_code}')
            raise ValueError

        if prefix:
            element_id = '{prefix}{sep}{element_id}'.format(prefix=prefix, sep=sep, element_id=element_id)
        if language_code:
            return '{element_id}{sep}{language_code}'.format(element_id=element_id, sep=sep, language_code=language_code.lower())
        else:
            return '{element_id}'.format(element_id=element_id)


    def clean_text(self, text):
        try:
            assert isinstance(text, str)
        except AssertionError:
            return text

        text, n = re.subn(string=text,
                          pattern='[ \t\r\v\f]*(\n|\\\\n)[ \t\r\v\f]*',
                          repl='  \n',
                          flags=re.MULTILINE)
        text, n = re.subn(string=text,
                          pattern='(  \n){2,}',
                          repl='  \n',
                          flags=re.MULTILINE)
        return (text.replace('"', "'")
                    .replace('\r', ' '))

    def find_worksheets(self, sheets):
        self.logger.info("Downloading NLU and model sheets...")
        worksheets = []
        for sheet_link in sheets:
            sheet = self.gc.open_by_url(sheet_link)
            worksheets.extend(sheet.worksheets())
        worksheets = {w.title : w for w in worksheets}
        return worksheets

    def load_target_records(self, worksheets, target_sheet):
        try:
            o = []
            found = False
            for key, worksheet in worksheets.items():
                if key.startswith(target_sheet) and key != 'Intents_french':
                    self.logger.info(f"Downloading {key} sheet...")
                    o.extend(worksheet.get_all_records())
                    found = True
            if not found:
                raise KeyError
            return o
        except KeyError:
            self.logger.error(f'Worksheet is missing: {target_sheet}')
            raise

    def load_all_records(self, worksheets, sheet_names):
        """ Pull the Google sheets and set attributes with each sheet's raw content"""

        self.logger.info("Load all records...")
        self.records_nlu = self.load_target_records(worksheets, sheet_names['nlu'])
        self.records_nlu_annotations = self.load_target_records(worksheets, sheet_names['annotations'])
        self.records_merge_tracker = self.load_target_records(worksheets, sheet_names['merge_tracker'])
        self.records_answers = self.load_target_records(worksheets, sheet_names['answers'])
        self.records_strings = self.load_target_records(worksheets, sheet_names['strings'])
        self.records_actions = self.load_target_records(worksheets, sheet_names['actions'])
        self.records_slots = self.load_target_records(worksheets, sheet_names['slots'])
        self.records_entities = self.load_target_records(worksheets, sheet_names['entities'])
        self.records_intents = self.load_target_records(worksheets, sheet_names['intents'])
        self.records_storybuilder = self.load_target_records(worksheets, sheet_names['storybuilder'])
        self.records_payloads = self.load_target_records(worksheets, sheet_names['payloads'])
        self.records_questions = self.load_target_records(worksheets, sheet_names['questions'])

        return None

    def process_all_records(self):
        """Process all raw content from sheets into tidy tables."""

        self.table_nlu = self.process_nlu_data(self.records_nlu)
        self.table_nlu_annotations = self.process_nlu_annotations(self.records_nlu_annotations,
                                                                  self.records_merge_tracker)

        self.table_answers = self.process_model_answers(self.records_answers)
        self.table_strings = self.process_model_strings(self.records_strings)
        self.table_buttoned_qs = self.process_model_buttoned_questions(self.records_questions,
                                                                       self.records_payloads)
        self.table_actions = self.process_model_actions(self.records_actions)
        self.table_slots = self.process_model_slots(self.records_slots)
        self.table_entities = self.process_model_entities(self.records_entities)
        self.table_intents = self.process_model_intents(self.records_intents)
        self.table_storybuilder = self.process_model_storybuilder(self.records_storybuilder)

        return True

    def process_nlu_annotations(self, records, merge_records=None):
        """ Process NLU annotated example records from Sheets into a dataframe.

        Args:
            records (list of dict): Records to process.
            merge_records(list of dict or None): Records indicating how to fix
                merged or removed annotation topics

        Returns:
            pandas.DataFrame: A dataframe with the columns:
                `sender_id`, `datetime`, `input_channel`,
                `prediction_topic`, `prediction_lang`, `prediction_confidence`,
                `intent_full_id`, `intent_topic`, `language`, `training_example`,
                `date_annotation`, `annotator_name`
        """

        self.logger.info("Processing NLU annotated examples records")
        if not records:
            return None

        if merge_records:
            self.logger.info(f'{len(records)} NLU annotations found')
            old2new = {r['old_name']: r['new_name'] for r in merge_records}
            for idx, record in enumerate(records):
                v = record['annotation_topic']
                records[idx]['annotation_topic'] = old2new.get(v, v)
            records = [r for r in records if r['annotation_topic'] != 'removed']
            records = [r for r in records if r['annotation_lang'].upper() in self.language_codes]
            self.logger.info(f'{len(records)} NLU annotations kept')

        df = pandas.DataFrame(records)
        df = (df.rename(columns={
                    'annotation_topic': 'intent_topic',
                    'annotation_lang': 'language',
                    'raw_text': 'training_example'})
                .filter(items=[
                    'sender_id', 'datetime', 'input_channel',
                    'prediction_topic', 'prediction_lang', 'prediction_confidence',
                    'intent_topic', 'language', 'training_example',
                    'date_annotation', 'annotator_name'])
                .replace('', numpy.nan))

        df['language'] = df['language'].str.lower()
        df['intent_full_id'] = df.apply(lambda row: self.make_id(element_id=row['intent_topic'],
                                                                 language_code=row['language']),
                                        axis=1)

        df = (df.reindex(columns=[
                'sender_id', 'datetime', 'input_channel',
                'prediction_topic', 'prediction_lang', 'prediction_confidence',
                'intent_full_id', 'intent_topic', 'language', 'training_example',
                'date_annotation', 'annotator_name'])
                .dropna(how='any', subset=['intent_topic', 'language']))

        n_examples = df['training_example'].size
        n_intents = df['intent_topic'].unique().size
        n_languages = len(self.language_codes)

        self.logger.info(
            f'{n_examples} training examples across {n_intents} x {n_languages} (topics x languages)')

        return df


    def process_nlu_data(self, records):
        """ Process NLU records from Sheets into a dataframe.

        Args:
            records (list of dict): Records to process.

        Returns:
            pandas.DataFrame: A dataframe with the columns:
                `intent_full_id`, `intent_topic`, `language`, `training_example`
        """

        self.logger.info("Processing NLU records")
        df = pandas.DataFrame(records)
        df = (df.rename(columns={NLU_INTENT_ID: 'intent_topic'})
                .filter(items=['intent_topic'] + self.language_codes)
                .replace('', numpy.nan)
                .dropna(how='all', subset=self.language_codes)
                .dropna(how='all', subset=['intent_topic'])
                .melt(id_vars=['intent_topic'],
                      value_vars=self.language_codes,
                      var_name='language',
                      value_name='training_example'))

        df['language'] = df['language'].str.lower()
        df['intent_full_id'] = df.apply(lambda row: self.make_id(element_id=row['intent_topic'],
                                                                 language_code=row['language']),
                                        axis=1)

        df = df.reindex(columns=['intent_full_id', 'intent_topic', 'language', 'training_example'])

        n_examples = df['training_example'].size
        n_intents = df['intent_topic'].unique().size
        n_languages = len(self.language_codes)

        self.logger.info(
            f'{n_examples} training examples across {n_intents} x {n_languages} (topics x languages)')

        return df


    def process_model_answers(self, records):
        """ Process answers records from Sheets into a dataframe.

        The result of this step is used to generate the FAQ stories in the
        processing step.

        Args:
            records (list of dict): Records to process.

        Returns:
            pandas.DataFrame: A dataframe with the columns:
                `utterance_full_id`, `utterance_topic`,
                `language`, `channel`, `image`, `utterance_text`
        """
        id_vars = ['utterance_topic', 'channel', 'image']

        self.logger.info("Processing model answers records")
        df = pandas.DataFrame(records)
        df = (df.rename(columns={UTT_ID: 'utterance_topic'})
                .filter(items=id_vars + self.language_codes)
                .replace('', numpy.nan)
                .dropna(how='all', subset=self.language_codes)
                .melt(id_vars=id_vars,
                      value_vars=self.language_codes,
                      var_name='language',
                      value_name='utterance_text'))

        df['language'] = df['language'].str.lower()
        df['utterance_text'] = df['utterance_text'].transform(self.clean_text)

        df['utterance_full_id'] = df.apply(lambda row: self.make_id(element_id=row['utterance_topic'],
                                                                    prefix='utter_answer',
                                                                    language_code=row['language']),
                                            axis=1)

        df = df.reindex(columns=['utterance_full_id', 'utterance_topic',
                                 'language', 'channel', 'image', 'utterance_text'])

        return df

    def process_model_strings(self, records):
        """ Process strings records from Sheets into a dataframe.

        Args:
            records (list of dict): Records to process.

        Returns:
            pandas.DataFrame: A dataframe with the columns:
                `utterance_full_id`, `utterance_topic`,
                `language`, `channel`, `image`, `utterance_text`
        """

        id_vars = ['utterance_topic', 'channel', 'image']

        self.logger.info("Processing model strings records")
        df = pandas.DataFrame(records)
        df = (df.rename(columns={UTT_ID: 'utterance_topic'})
                .filter(items=id_vars + self.language_codes)
                .melt(id_vars=id_vars,
                      value_vars=self.language_codes,
                      var_name='language',
                      value_name='utterance_text')
                .replace('', numpy.nan))
        df['language'] = df['language'].str.lower()
        df['utterance_text'] = df['utterance_text'].transform(self.clean_text)
        df['utterance_full_id'] = df.apply(lambda row: self.make_id(element_id=row['utterance_topic'],
                                                                    prefix='utter',
                                                                    language_code=row['language']),
                                 axis=1)
        df = df.reindex(columns=['utterance_full_id', 'utterance_topic',
                                 'language', 'channel', 'image', 'utterance_text'])

        return df


    def _process_questions_text(self, records, keep_extra_cols=False):
        """ Process text for buttoned questions

        Essentially just melt records into a df suitable for joining.

        Args:
            records (list of dict): Questions records.
            keep_extra_cols (bool): Whether to keep the non-essential-for-rasa
                output dataframe's columns

        Returns:
            pandas.DataFrame: A dataframe with the columns:
                `utterance_topic`, `payload`, `language`, `utterance_text`
                as well as any other columns present in `records` if `keep_extra_cols` is True
        """

        self.logger.info("Processing model buttoned questions utterances records")

        new_records = []
        all_cols = set()
        for record in records:
            all_cols.update(record.keys())
            dup = [x if x else '' for x in record[PAYLOAD].replace(' ', '').split(',')]
            for val in dup:
                o = record.copy()
                o[PAYLOAD] = val
                new_records.append(o)

        var_cols = ['utterance_topic', 'channel', 'image', 'payload']
        if keep_extra_cols:
            var_cols = list(set(var_cols) - set(self.language_codes))

        wanted_cols = var_cols + self.language_codes

        df = pandas.DataFrame(new_records)
        df = (df.rename(columns={UTT_ID: 'utterance_topic',
                                 PAYLOAD: 'payload'})
                .filter(items=wanted_cols))


        w = (df.melt(id_vars=var_cols,
                     var_name='language',
                     value_name='utterance_text',
                     value_vars=[col for col in self.language_codes])
               .drop_duplicates()
               .reset_index(drop=True))
        w['language'] = w['language'].str.lower()

        return w

    def _process_questions_payloads(self, records):
        """ Process payloads for buttoned questions.

        Essentially just melt records into a df suitable for joining.
        Also add a payload-less for each language to deal with those utterance
        tables containing rows without payload list (open-ended questions)

        Args:
            records (list of dict): Button payloads records

        Returns:
            pandas.DataFrame: A dataframe with the columns:
                `payload_full_id`, `payload`,
                `language`, `channel`, `image`, `button_text`
        """

        self.logger.info("Processing model buttoned questions payloads records")

        df = pandas.DataFrame(records)
        df = df.rename(columns={PAYLOAD: 'payload'})

        v = (df.melt(id_vars=['payload'],
                     var_name='language',
                     value_name='button_text',
                     value_vars=[col for col in self.language_codes]))
        v['language'] = v['language'].str.lower()

        v['payload_full_id'] = v.apply(lambda row: self.make_id(element_id=row['payload'],
                                                                language_code=row['language']),
                                       axis=1)

        for lang in self.language_codes:
            v = v.append({'payload': '',
                          'language': lang.lower(),
                          'button_text': '',
                          'payload_full_id': ''},
                         ignore_index=True)

        return v

    def _join_questions_and_payloads(self,
                                     df_questions,
                                     df_payloads,
                                     keep_extra_cols=False):

        df = (df_questions.set_index(['payload', 'language'])
                          .join(df_payloads.set_index(['payload', 'language']))
                          .reset_index()
                          .sort_values(by=['utterance_topic', 'language', 'channel'])
                          .reset_index(drop=True)
                          .replace('', numpy.nan))

        df['utterance_full_id'] = df.apply(lambda row: self.make_id(element_id=row['utterance_topic'],
                                                                    prefix='utter',
                                                                    language_code=row['language']),
                                 axis=1)

        # Payload names currently depend on
        df['payload'] = df['payload_full_id']

        if keep_extra_cols:
            cols = df.columns
        else:
            cols = ['utterance_full_id', 'utterance_topic',
                    'language', 'channel', 'image',
                    'utterance_text', 'button_text', 'payload']

        df = df.reindex(columns=cols)
        return df

    def process_model_buttoned_questions(self,
                                         records_questions,
                                         records_payloads,
                                         keep_extra_cols=False):
        """ Process buttoned questions from Sheets into a dataframe.

        Args:
            records_questions (list of dict): Questions text records.
            records_payloads (list of dict): Button payloads records
            keep_extra_cols (bool): Whether to keep the non-essential-for-rasa
                output dataframe's columns

        Returns:
            pandas.DataFrame: A dataframe with the columns:
                `utterance_full_id`, `utterance_topic`,
                `language`, `channel`, `image`,
                `utterance_text`, `button_text`, `payload`
                as well as any other columns present in `records_utterances` if
                `keep_extra_cols` is True
        """

        self.logger.info("Processing model buttoned questions")

        df_questions = self._process_questions_text(records_questions,
                                                    keep_extra_cols=keep_extra_cols)
        df_payloads = self._process_questions_payloads(records_payloads)
        df = self._join_questions_and_payloads(df_questions,
                                               df_payloads,
                                               keep_extra_cols=keep_extra_cols)

        return df


    def process_model_actions(self, records):
        """ Process actions records from Sheets into a dataframe.

        Args:
            records (list of dict): Records to process.

        Returns:
            pandas.DataFrame: A dataframe with the columns:
                `action_full_id`, `action_id`, `language`, `action_type`
        """

        self.logger.info("Processing model actions records")
        new_records = []
        for record in records:
            if record[MULTILINGUAL_ID] == 'TRUE':
                for lang in self.language_codes:
                    o = record.copy()
                    o['language'] = lang.lower()
                    new_records.append(o)
            else:
                record['language'] = ''
                new_records.append(record)

        df = pandas.DataFrame(new_records)
        df = (df.rename(columns={ACT_ID: 'action_id'})
                .filter(items=['action_id', 'language']))
        df['action_full_id'] = df.apply(lambda row: self.make_id(element_id=row['action_id'],
                                                                 language_code=row['language']),
                                        axis=1)
        df['action_type'] = df['action_id'].str.extract('(form|action)')

        df = (df.replace('', numpy.nan)
               .reindex(columns=['action_full_id', 'action_id', 'language', 'action_type']))

        return df


    def process_model_slots(self, records):
        """ Process slots records from Sheets into a dataframe.

        Args:
            records (list of dict): Records to process.

        Returns:
            pandas.DataFrame: A dataframe with the columns:
                `slot_full_id`, `slot_id`, `language`, `slot_type`
        """

        # For values column, split string on ",", and trim whitespace

        self.logger.info("Processing model slots records")
        new_records = []
        for record in records:
            if not record['slot_id']:
                continue
            if record['multilingual'] == 'TRUE':
                for lang in self.language_codes:
                    o = record.copy()
                    o['language'] = lang.lower()
                    new_records.append(o)
            else:
                record['language'] = ''
                new_records.append(record)

        df = pandas.DataFrame(new_records)
        cols = [
            'slot_id', 'slot_type', 'language',
            'auto_fill', 'influence_conversation', 'initial_value',
            'values', 'min_value', 'max_value'
        ]
        df['auto_fill'] = df['auto_fill'] == 'TRUE'
        df['influence_conversation'] = df['influence_conversation'] == 'TRUE'
        df = df.filter(items=cols)

        df['slot_full_id'] = df.apply(lambda row: self.make_id(element_id=row['slot_id'],
                                                               language_code=row['language']),
                                      axis=1)

        df = (df.replace('', numpy.nan)
               .reindex(columns=['slot_full_id'] + cols))

        return df

    def duplicate_record(self, record, key, values, lower=False):
        if len(values) == 1:
            return [record]
        l = []
        for val in values:
            val = val.lower() if lower else val
            o = record.copy()
            o[key] = val
            l.append(o)
        return l


    def process_model_entities(self, records):
        """ Process entities records from Sheets into a dataframe.

        Args:
            records (list of dict): Records to process.

        Returns:
            pandas.DataFrame: A dataframe with the columns:
                `entity_id`
        """

        def make_full_pattern(l):
            """ Merge patterns together: \b(p1|p2|...)\b"""
            j = '|'.join(l)
            p = f"\\b({j})\\b"
            return re.compile(p, flags=re.IGNORECASE)

        self.logger.info("Processing model entity records")
        if not records:
            self.logger.warning('No entities found')
            return None

        new_records = []
        for record in records:
            if record['language_pattern'] == '*':
                dup = self.language_codes
            else:
                dup = ''.join(record['language_pattern'].strip()).split(',')
            new_records.extend(self.duplicate_record(record, 'language_pattern', dup, lower=True))

        df = pandas.DataFrame(new_records)
        df = (df.filter(items=['entity_id',
                              'language_pattern',
                              'capture_pattern',
                              'synonym'])
                .groupby(['entity_id', 'language_pattern', 'synonym'])
                .aggregate({'capture_pattern' : make_full_pattern})
                .reset_index()
                .filter(items=['entity_id',
                              'language_pattern',
                              'capture_pattern',
                              'synonym']))

        return df

    def process_model_intents(self, records):
        """ Process intents records from Sheets into a dataframe.

        To write the intents in `domain.yaml`, only the `intent_topic` column of
            the output dataframe is needed: the other columns are here for other
            potential purposes.

        Args:
            records (list of dict): Records to process.

        Returns:
            pandas.DataFrame: A dataframe with the columns:
                `intent_topic`, `topic_master`, `topic_primary`, `topic_secondary`
        """

        self.logger.info("Processing model intents records")
        df = pandas.DataFrame(records)
        df = (df.rename(columns={INTENT_ID: 'intent_topic',
                                 INTENT_TOPIC_MASTER: 'topic_master',
                                 INTENT_TOPIC_PRIMARY: 'topic_primary',
                                 INTENT_TOPIC_SECONDARY: 'topic_secondary'})
                .filter(items=['intent_topic', 'topic_master', 'topic_primary', 'topic_secondary']))

        return df


    def process_model_storybuilder(self, records):
        """ Process storybuilder records from Sheets into a dataframe.

        Args:
            records (list of dict): Records to process.

        Returns:
            pandas.DataFrame: A dataframe with the columns:
                `story_id`, `story_trigger`, `language`, `turn_number`, `turn_taker`, `turn_action`, `story_type`
        """

        self.logger.info("Processing storybuilder records")
        df = pandas.DataFrame(records)

        return df
