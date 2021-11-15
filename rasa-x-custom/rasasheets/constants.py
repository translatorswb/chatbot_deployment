#! /usr/bin/env python3

# Eventually this needs to be re-vamped

# ===== Google Sheets Links =====
# Uji - DRC
# The production model: answers, questions, strings, actions, slots, etc
UJI_MODEL_SHEET_LINK = "https://docs.google.com/spreadsheets/d/1qYkomnPq9mYUxCVJsCD2j7IJm_bx9BeO0VQcBvmVz1o"
# The production training data
UJI_NLU_SHEET_LINK = "https://docs.google.com/spreadsheets/d/1MHGaSdT7dNcj2bMX8-HUYks4apLUbgTQwRi3sj67a9k"

# The development model: answers, questions, strings, actions, slots, etc
UNA_MODEL_SHEET_LINK = "https://docs.google.com/spreadsheets/d/1_k5C3vDsDlsXsR36471FyyT9iRLhMu-5nDL2weEQNZc"
# The development training data
UNA_NLU_SHEET_LINK = "https://docs.google.com/spreadsheets/d/1CMbVidNpqT3xA6HMxGjYa6o9zdtC2IvbpD4NQmxX5-o"

# Shehu - Nigeria
# The production model: answers, questions, strings, actions, slots, etc
SHEHU_MODEL_SHEET_LINK = "https://docs.google.com/spreadsheets/d/1dgWSkbLn-Sy5WNnZrNIxqUR0R-wW-KIFDskYrb_wpb0"
# The production training data
SHEHU_NLU_SHEET_LINK = "https://docs.google.com/spreadsheets/d/17jKT6O1GFQgQOWzFhDe8jEEbJBkUVhe7HK8eSNlbjlU"

# IOM - Ecuador, Peru, Mexico
# The production model: answers, questions, strings, actions, slots, etc
IOM_MODEL_SHEET_LINK = "https://docs.google.com/spreadsheets/d/1IrzAWQrmf-hwSAj_F1JcAfSHFU0DADB1wjz-NxQoN2k"
# The production training data
IOM_NLU_SHEET_LINK = "https://docs.google.com/spreadsheets/d/1fLfAhvyxQb-Q3dZ7JuhPLAHZuDXpJZZX-fGiEUfBB0M"


# ===== Google Sheets Model Specifications =====

# ----- (All) Possible languages -----
LANGUAGES = ['ENG', 'FRA', 'HAU', 'KAU', 'LIN', 'SHU', 'SPA', 'SWC']

# ----- Sheet names -----
SHEET_NAMES = {
    'nlu': 'NLU',
    'annotations': 'annotated_examples',
    'merge_tracker': 'merge_tracker',
    'answers': 'Answers',
    'strings': 'Strings',
    'questions': 'Questions',
    'payloads': 'Payloads',
    'actions': 'ActionsForms',
    'slots': 'Slots',
    'entities': 'Entities',
    'intents': 'Intents',
    'storybuilder': 'Storybuilder'
}

NAMES2KIND = {
    'NLU': 'nlu',
    'annotated_examples': 'annotations',
    'Answers': 'answers',
    'Strings': 'strings',
    'Questions': 'questions',
    'Payloads': 'payloads',
    'ActionsForms': 'actions',
    'Slots': 'slots',
    'Entities': 'entities',
    'Intents': 'intents',
    'Storybuilder': 'storybuilder'
}



# # NLU sheets
# SHEET_NAME_NLU = 'NLU'
# SHEET_NAME_ANNOTATIONS = 'annotated_examples'
#
# # Model sheets
# SHEET_NAME_ANSWERS = 'Answers'
# SHEET_NAME_STRINGS = 'Strings'
# SHEET_NAME_QUESTIONS = 'general_questions'
# SHEET_NAME_PAYLOADS = 'general_payloads'
# SHEET_NAME_ACTIONS = 'ActionsForms'
# SHEET_NAME_SLOTS = 'Slots'
# SHEET_NAME_GENERAL_SLOTS = 'general_slots'
# SHEET_NAME_ENTITIES = 'Entities'
# SHEET_NAME_GENERAL_ENTITIES = 'general_entities'
# SHEET_NAME_INTENTS = 'Intents'
# # SHEET_NAME_STORYBUILDER = 'StoryBuilder'
# SHEET_NAME_STORYBUILDER = 'general_story_builder'

# ----- Column IDs -----
NLU_INTENT_ID = 'Intent'

UTT_ID = 'Utterance ID'
PAYLOAD = 'Payload'

ACT_ID = 'Action ID'
MULTILINGUAL_ID = 'Multilingual'

SLOT_ID = 'Slot ID'
SLOT_TYPE = 'Type'

ENTITY_ID = 'Entity ID'

INTENT_ID = 'Intent ID'
INTENT_TOPIC_MASTER = 'Topic_master'
INTENT_TOPIC_PRIMARY = 'Topic_primary'
INTENT_TOPIC_SECONDARY = 'Topic_secondary'

# ----- Prefixes -----
MYTH_PREFIX = '_myth_'
MYTH_QUERY_FORM_ID = 'form_myth_source'    # Form that asks "Where did you hear that myth?"
#ASK_FEEDBACK_FORM_ID = "form_feedback"
ASK_FEEDBACK_FORM_ID = "action_get_faq_ctr"
ANYTHING_ELSE_STRING_ID = 'anything_else'  # Anything else I can help you with?

# ----- Quiz column names -----
SHEET_NAME_QUIZ = 'Quiz'
QUIZ_LEVEL = 'Quiz_Level'
QUIZ_QUESTION_INDEX = 'Quiz_Question_Index'
QUIZ_KEY = 'Quiz_Key'
QUIZ_ANSWER_PREFIX = 'Quiz_Feedback_'

# ----- Other -----
ANSWER_PREFIX = "answer_"
UNIQUE_SLOTS = {"requested_slot": "unfeaturized"}
NO_PAYLOAD_TAKE_FROM_BUTTON_MARKER = "no-payload-button_" #When the payload will be the button value
