import re
import json
import pandas
from collections import Counter
from .setup_logging import logging
from .constants import PAYLOAD, SHEET_NAME_QUIZ, QUIZ_LEVEL, QUIZ_QUESTION_INDEX, QUIZ_KEY, QUIZ_ANSWER_PREFIX

class Quiz(object):

    def __init__(self, sm):
        self.logger = logging.getLogger(__name__)
        self.logger.info('Building quiz feature...')

        self.quiz_records = self.make_quiz_records(sm.worksheets)

        self.quiz_data = self.prepare_output_quiz_data(self.quiz_records,
                                                       sm.language_codes)

        self.quiz_questions = self.make_quiz_questions(self.quiz_records)

        self.quiz_buttoned_qs = self.make_quiz_buttoned_qs(sm,
                                                           self.quiz_questions,
                                                           sm.records_payloads)

        self.updated_buttoned_qs = self.concatenate_buttoned_qs(sm.table_buttoned_qs,
                                                                self.quiz_buttoned_qs)

        # self.quiz_answers = self.make_quiz_answers(self.quiz_records)

    # def modify_record(self, record):
    #     for lang in self.language_codes:
    #         record[lang] = record.pop(f'{QUIZ_ANSWER_PREFIX}{lang}')
    #     return record

    def make_quiz_records(self, worksheets, quiz_sheet_name=SHEET_NAME_QUIZ):
        quiz_records = worksheets[quiz_sheet_name].get_all_records()

        question_index_counter = Counter()
        for idx, record in enumerate(quiz_records):
            question_level = record[QUIZ_LEVEL]

            question_index = record[QUIZ_QUESTION_INDEX]
            question_index_counter[question_index] += 1

            response_index = question_index_counter[question_index]

            correct_answer = True if record[QUIZ_KEY] == 'TRUE' else False

            quiz_records[idx][PAYLOAD] = '/affirm, /deny'
            quiz_records[idx]['utterance_topic'] = (
                f"ask_quiz_level_{question_level}_question_{question_index}")
            quiz_records[idx]['id'] = (
                 f"ask_quiz_level_{question_level}_question_{question_index}_{response_index}")
            quiz_records[idx][QUIZ_KEY] = correct_answer

        return quiz_records

    def make_quiz_questions(self, records):
        # We need a facebook version with quick_replies for each question
        # ***** 'image' column is assumed to be in the quiz sheet *****
        quiz_questions = [{k: v for k, v in record.items() if QUIZ_ANSWER_PREFIX not in k}
             for record in records]

        o = []
        # We add 2 versions of each record: a fb one (quick_replies will be used)
        # AND a normal one
        for record in quiz_questions:
            record['channel'] = ''
            o.append({**record})
            o.append({**record,
                      'channel': 'facebook'})

        return o


    def make_quiz_buttoned_qs(self, sm, quiz_questions, records_payloads):
        df = sm.process_model_buttoned_questions(quiz_questions,
                                                 records_payloads)
        return df

    def concatenate_buttoned_qs(self, buttoned_qs, quiz_buttoned_qs):
        df = (pandas.concat([buttoned_qs,
                             quiz_buttoned_qs])
                    .reset_index(drop=True)
                    .dropna(subset=['utterance_text']))
        return df

    # def make_quiz_answers(self, records):
    #     quiz_answers = [{k: v for k, v in record.items()
    #                     if re.search(f'({QUIZ_ANSWER_PREFIX}|utterance_topic|{PAYLOAD})', k)}
    #                     for record in records]
    #
    #     return [self.modify_record(record) for record in quiz_answers]

    def prepare_output_quiz_data(self, quiz_records, language_codes):
        o = []
        for idx, record in enumerate(quiz_records):
            r = {
                'level' : record[QUIZ_LEVEL],
                'question_index' : record[QUIZ_QUESTION_INDEX],
                'key' : record[QUIZ_KEY],
                'id' : f"utter_{record['id']}",
                'utterance_topic' : f"utter_{record['utterance_topic']}",
                'question' : {lang: record[lang] for lang in language_codes},
                'answer': {lang: record[f'{QUIZ_ANSWER_PREFIX}{lang}'] for lang in language_codes}
            }
            o.append(r)
        return o

    def write_quiz_to_file(self, filename):
        self.logger.info(f'Writing quiz data to {filename}')
        with open(filename, 'w') as f:
            json.dump(self.quiz_data,
                      f,
                      indent=2)
        return None
