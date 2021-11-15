import gspread
import sys, re
from settings import PWD

def generate_files(data, repo_id):
    #print(sys.argv[1:])

    LANGUAGES = data['lang']
    IS_MULTILINGUAL = len(LANGUAGES) > 1
    bot_strings_sheet = data['bot_strings_sheet']
    nlu_sheet = data['nlu_sheet']


    DOMAIN_YML_FILE = f'/app/git/{repo_id}/domain.yml'
    NLU_MD_FILE = f'/app/git/{repo_id}/data/nlu.md'
    STORIES_MD_FILE = f'/app/git/{repo_id}/data/stories.md'
    TESTS_MD_FILE = 'conversation_tests.md'


    #Sheet links
    #SHEET_LINK = 'https://docs.google.com/spreadsheets/d/136ZNF-TkD8_6JOBnvhEjKBbcy-IzNcvFaHtSQ2M1Iig/edit#gid=1249386078'
    MODEL_SHEET_LINK = data['bot_strings_sheet']
    NLU_SHEET_LINK = nlu_sheet = data['nlu_sheet']

    #Other constants
    SESSION_EXPIRATION_TIME = '60'
    CARRY_OVER_SLOTS_TO_NEW_SESSION = 'true'
    IS_MULTILINGUAL = len(LANGUAGES) > 1


    # ### Sheet labels etc.

    # In[33]:


    #Column IDs
    UTT_ID = 'Utterance ID'
    ACT_ID = 'Action ID'
    MULTILINGUAL_ID = 'Multilingual'
    SLOT_ID = 'Slot ID'
    ENTITY_ID = 'Entity ID'
    INTENT_ID = 'Intent ID'
    PAYLOAD = 'Payload'
    SLOT_TYPE = 'Type'
    STORY_TURN_TAKER_PREFIX = 'Turn taker'
    STORY_TURN_ACTION_PREFIX = 'Turn action'
    STORY_TITLE = 'Story Title'

    MYTH_PREFIX = '_myth_'
    MYTH_QUERY_FORM_ID = 'form_myth_source'    # Form that asks "Where did you hear that myth?"
    #ASK_FEEDBACK_FORM_ID = "form_feedback"
    ASK_FEEDBACK_FORM_ID = "action_get_faq_ctr"
    ASK_DISEASE_FORM_ID = "form_disease_name"
    ANYTHING_ELSE_STRING_ID = 'anything_else'  # Anything else I can help you with?

    STORY_TURN_USER_PREFIX = 'user'
    STORY_TURN_BOT_PREFIX = 'bot'

    STORY_TURN_USER_LABEL = 'user:'
    STORY_TURN_BOT_RESPONSE_LABEL = 'bot_response:'
    STORY_TURN_BOT_ACTION_LABEL = 'bot_action:'

    #Other
    ANSWER_PREFIX = "answer_"
    UNIQUE_SLOTS = {"requested_slot": "unfeaturized"}
    NO_PAYLOAD_TAKE_FROM_BUTTON_MARKER = "no-payload-button_" #When the payload will be the button value


    # In[5]:


    def clean_text(text):
        clean_text = text.replace('\n', ' ')
        clean_text = clean_text.replace('"', "'")
        clean_text = clean_text.replace('\r', ' ')
        return clean_text


    def annotate_disease(s):
        def repl_disease(m):
            return '[{captured}]{{"entity": "disease", "value": "{disease}"}}'.format(captured=m.group(0), disease=disease)

        p_already_annotated = re.compile('\[.*?\]\(disease\)')
        if re.search(pattern=p_already_annotated, string=s):
            print('training example already annotated')
            return s

        p_covid = re.compile('\\b(corona( ?virus)?|coronavii?rus|coronar|covid(-|=)?(19|10)?|c19|c(-|=)19|virusi ya corona(virus)?)\\b', flags=re.IGNORECASE)
        p_ebola = re.compile('\\b(ebola|virus ebola|virusi ya ebola)\\b', flags=re.IGNORECASE)

        disease = 'covid'
        s, n = re.subn(pattern=p_covid, string=s, repl=repl_disease)

        disease = 'ebola'
        s, n = re.subn(pattern=p_ebola, string=s, repl=repl_disease)

        return s

    def strip_annotation(s):
        def repl_annotation(m):
            return '{captured}'.format(captured=m.group(1))

        # def find_brackets(s):
        #     p = re.compile('(\[|\]|)')

        p_annotation = re.compile('\[\\b(.*?)\\b\]\{"entity": "disease", "value": "(covid|ebola)"\}')

        s, n = re.subn(pattern=p_annotation, string=s, repl=repl_annotation)

        return s



    # ### Connect to spreadsheets

    # In[6]:


    gc = gspread.service_account()


    # In[7]:


    #Bot strings
    try:
        sheet = gc.open_by_url(MODEL_SHEET_LINK)
        answers_worksheet = sheet.worksheet("Answers")
        strings_worksheet = sheet.worksheet("Strings")
        buttoned_qs_worksheet = sheet.worksheet("Questions")
        actions_worksheet = sheet.worksheet("ActionsForms")
        slots_worksheet = sheet.worksheet("Slots")
        intents_worksheet = sheet.worksheet("Intents")
        storybuilder_worksheet = sheet.worksheet("StoryBuilder")
        entities_worksheet = sheet.worksheet("Entities")
    except Exception as e:
        print("Cannot access spreadsheet")
        print(e)
        sys.exit()


    # In[8]:


    #Training data
    try:
        sheet = gc.open_by_url(NLU_SHEET_LINK)
        nlu_worksheet = sheet.get_worksheet(0)
    except Exception as e:
        print("Cannot access spreadsheet")
        print(e)
        sys.exit()


    # ### Read answers

    # In[9]:


    answers_in_dicts = answers_worksheet.get_all_records()

    def read_answers(lang_code):
        return {ANSWER_PREFIX + answer[UTT_ID]:clean_text(answer[lang_code]) for answer in answers_in_dicts}

    all_answers = {lang:read_answers(lang) for lang in LANGUAGES}


    # ### Read other strings

    # In[10]:


    strings_in_dicts = strings_worksheet.get_all_records()

    def read_strings_to_dict(lang_code):
        data = {}
        for string in strings_in_dicts:
            if not string[UTT_ID] in data:
                data[string[UTT_ID]] = []
            data[string[UTT_ID]].append(clean_text(string[lang_code]))
        return data

    all_strings = {lang:read_strings_to_dict(lang) for lang in LANGUAGES}


    # ### Read buttoned questions

    # In[34]:


    buttoned_qs_in_dicts = buttoned_qs_worksheet.get_all_records()

    def read_buttoned_qs_to_dict(lang_code):
        data = {}

        for q in buttoned_qs_in_dicts:
            if not q[UTT_ID] in data:
                data[q[UTT_ID]] = {'string':q[lang_code], 'buttons':{}}
                button_no = 0
            if q[PAYLOAD]:
                data[q[UTT_ID]]['buttons'][q[PAYLOAD]] = q['button_' + lang_code]
            else:
                data[q[UTT_ID]]['buttons'][NO_PAYLOAD_TAKE_FROM_BUTTON_MARKER + str(button_no)] = q['button_' + lang_code]
                button_no += 1
        return data

    all_buttoned_qs = {lang:read_buttoned_qs_to_dict(lang) for lang in LANGUAGES}


    # ### Read forms and actions

    # In[12]:


    actions_in_dicts = actions_worksheet.get_all_records()

    def read_forms_and_actions():
        actions = [entry[ACT_ID] for entry in actions_in_dicts if entry[ACT_ID].startswith('action')]
        forms = [entry[ACT_ID] for entry in actions_in_dicts if entry[ACT_ID].startswith('form')]
        return forms, actions

    forms, actions = read_forms_and_actions()


    # In[13]:


    actions_in_dicts = actions_worksheet.get_all_records()

    def read_forms_and_actions_ids():
        forms_ids = []
        actions_ids = []

        multilingual_actions = [entry[ACT_ID] for entry in actions_in_dicts if entry[ACT_ID].startswith('action') and entry[MULTILINGUAL_ID] == 'TRUE']
        multilingual_forms = [entry[ACT_ID] for entry in actions_in_dicts if entry[ACT_ID].startswith('form') and entry[MULTILINGUAL_ID] == 'TRUE']

        unilingual_actions = [entry[ACT_ID] for entry in actions_in_dicts if entry[ACT_ID].startswith('action') and entry[MULTILINGUAL_ID] == 'FALSE']
        unilingual_forms = [entry[ACT_ID] for entry in actions_in_dicts if entry[ACT_ID].startswith('form') and entry[MULTILINGUAL_ID] == 'FALSE']

        for form in multilingual_forms:
            for language in LANGUAGES:
                forms_ids.append(form + "_" + language.lower())

        for action in multilingual_actions:
            for language in LANGUAGES:
                actions_ids.append(action + "_" + language.lower())

        forms_ids.extend(unilingual_forms)
        actions_ids.extend(unilingual_actions)

        return forms_ids, actions_ids

    forms_ids, actions_ids = read_forms_and_actions_ids()


    # ### Read slots

    # In[14]:


    slots_in_dicts = slots_worksheet.get_all_records()

    slots = {entry[SLOT_ID]:entry[SLOT_TYPE] for entry in slots_in_dicts}


    ### Read Entities

    entities_in_dicts = entities_worksheet.get_all_records()

    entities = [entry[ENTITY_ID] for entry in entities_in_dicts]


    # ### Read intents

    # In[15]:


    from collections import Counter

    intents_in_dicts = intents_worksheet.get_all_records()

    intents = [entry[INTENT_ID] for entry in intents_in_dicts]

    dupl = [i for i, cnt in Counter(intents).items() if cnt > 1]

    if len(dupl) > 0:
        print("WARNING: Duplicate intent ids in Intents sheet: %s"%dupl)


    # ### Read stories

    # In[16]:


    #From StoryBuilder
    stories_in_lists = storybuilder_worksheet.get_all_records()

    stories = {}
    for story in stories_in_lists:
        if story[STORY_TITLE]:
            stories[story[STORY_TITLE]] = {'role_list':[], 'action_list':[]}
            #print(story[STORY_TITLE], end = '\t')
            turn_no = 1
            while True:

                turn_taker_key = STORY_TURN_TAKER_PREFIX + ' ' + str(turn_no)
                turn_action_key = STORY_TURN_ACTION_PREFIX + ' ' + str(turn_no)

                if story[turn_taker_key] and story[turn_action_key]:
                    #print(story[turn_taker_key], end = ' ')
                    stories[story[STORY_TITLE]]['role_list'].append(story[turn_taker_key])
                    stories[story[STORY_TITLE]]['action_list'].append(story[turn_action_key])
                else:
                    if not stories[story[STORY_TITLE]]['role_list']:
                        stories.pop(story[STORY_TITLE])
                    break

                turn_no += 1
            #print("")


    # ### Read NLU training data

    # In[17]:


    nlu_in_dicts = nlu_worksheet.get_all_records()

    def read_questions(lang_code):
        nlu = {}
        for i, question in enumerate(nlu_in_dicts):
            if not question['Intent']:
                print("WARNING: Empty intent id in line %i of NLU training data sheet"%(i + 2))
            else:
                if not question['Intent'] in nlu:
                    nlu[question['Intent']] = []
                if question[lang_code] and not question[lang_code].isspace() and question[lang_code] not in nlu[question['Intent']]:
                    nlu[question['Intent']].append(question[lang_code])

        #Check if each intent has at least two training examples
        for intent in nlu:
            if len(nlu[intent]) < 2:
                print("WARNING: In NLU training data, intent %s_%s has less than two training examples"%(intent, lang_code.lower()) )
            if intent not in intents:
                print("WARNING: Intent %s listed in NLU training data is not specified in Chatbot models sheet"%(intent) )
                print("         Adding {intent} to the intents list to be written to domain.yml".format(intent=intent))
                intents.append(intent)

        return nlu

    all_nlus = {lang:read_questions(lang) for lang in LANGUAGES}

    # Deduplicate intents
    print('LENGTH OF INTENTS IS {}'.format(len(intents)))
    intents = list(set(intents))
    print('LENGTH OF INTENTS AFTER DEDUP IS {}'.format(len(intents)))

    # ## Make Rasa bot files

    # ### domain.yml

    # In[35]:


    with open(DOMAIN_YML_FILE, 'w') as f:
        lang_list = '-'.join(LANGUAGES).upper()

        #write intents
        f.write('intents:\n\n')
        for language in LANGUAGES:
            lang_specific_intents = ['{intent}_{language}'.format(intent=intent,
                                                                language=language.lower())
                                    for intent in intents]

            for intent_full_id in sorted(lang_specific_intents):
                f.write('  - {intent_full_id}\n'.format(intent_full_id=intent_full_id))

        #write forms
        f.write('\nforms:\n')
        for form_id in forms_ids:
            f.write('  - ' + form_id + '\n')

        #write actions
        f.write('\nactions:\n')
        for action_id in actions_ids:
            f.write('  - ' + action_id + '\n')


        #write entities
        f.write('\nentities:\n')
        for entity in entities:
            f.write('  - ' + entity + '\n')

        #write slots
        f.write('\nslots:\n')
        for language in LANGUAGES:
            for slot in slots:
                if slot not in UNIQUE_SLOTS:
                    slot_id = slot + '_' + language.lower()
                    f.write('  ' + slot_id + ':\n')
                    f.write('    ' + 'type: ' + slots[slot] + '\n')
        for slot in UNIQUE_SLOTS:
            f.write('  ' + slot + ':\n')
            f.write('    ' + 'type: ' + UNIQUE_SLOTS[slot] + '\n')

        #write responses: answers, questions etc.
        f.write('\nresponses:\n\n')

        #f.write('  utter_answer_Intent:\n  - text: "%s"\n\n'%lang_list)

        for language in LANGUAGES:
            #STRINGS, QUESTIONS
            for intent in all_strings[language]:
                intent_id = intent + '_' + language.lower()

                response_id = 'utter_' + intent_id
                f.write('    %s:\n'%response_id)

                try:
                    answers = all_strings[language][intent]
                except:
                    print("Can't find intent %s in responses for %s"%(intent, language))
                    answers = 'TEMP ANSWER'

                for answer in answers:
                    f.write('      - text: "%s"\n'%(answer))
                f.write('\n')

            #BUTTONED QUESTIONS
            for buttoned_qs in all_buttoned_qs[language]:
                intent_id = buttoned_qs + '_' + language.lower()

                response_id = 'utter_' + intent_id
                f.write('    %s:\n'%response_id)
                f.write('      - text: "%s"\n'%(all_buttoned_qs[language][buttoned_qs]['string']))

                if not 'no-payload-button_0' in all_buttoned_qs[language][buttoned_qs]['buttons']:
                    f.write('        buttons:\n')

                    for button in all_buttoned_qs[language][buttoned_qs]['buttons']:
                        title = all_buttoned_qs[language][buttoned_qs]['buttons'][button]

                        f.write('        - title: "%s"\n'%title)
                        if button.startswith("/"):
                            f.write('          payload: "%s_%s"\n'%(button, language.lower()))
                        elif button.startswith(NO_PAYLOAD_TAKE_FROM_BUTTON_MARKER):
                            f.write('          payload: "%s"\n'%(title))
                        else:
                            if button in all_nlus[language]:
                                f.write('          payload: "%s"\n'%(all_nlus[language][button][0]))
                            else:
                                f.write('          payload: "%s"\n'%(button))





                f.write('\n')

            #ANSWERS
            for intent in all_answers[language]:
                intent_id = intent + '_' + language.lower()

                response_id = 'utter_' + intent_id
                try:
                    answer = all_answers[language][intent]
                except:
                    print("Can't find intent %s in responses for %s"%(intent, language))
                    answer = 'TEMP ANSWER'
                f.write('    %s:\n      - text: "%s"\n\n'%(response_id, answer))


        #Write tracker session configuration
        f.write('session_config:\n')
        f.write('  session_expiration_time: %s\n'%SESSION_EXPIRATION_TIME)
        f.write('  carry_over_slots_to_new_session: %s\n'%CARRY_OVER_SLOTS_TO_NEW_SESSION)

    print("Domain.yml written.")


    # ### nlu.md

    # In[126]:


    nlu_intent_ids = []
    with open(NLU_MD_FILE, 'w') as f:
        f.write("\n")

        for language in LANGUAGES:
            for nlu_intent in all_nlus[language]:
                nlu_intent_id = nlu_intent + '_' + language.lower()

                if len(all_nlus[language][nlu_intent]) > 0:
                    nlu_intent_ids.append(nlu_intent_id)

                    f.write('## intent:%s\n'%nlu_intent_id)

                    for question in all_nlus[language][nlu_intent]:
                        if question and not question.isspace():
                            question = annotate_disease(question)
                            f.write('- %s\n'%question)

                    f.write('\n')

    #Check if nlu covers all intents
    for language in LANGUAGES:
        for intent in intents:
            intent_id = intent + '_' + language.lower()
            if not intent_id in nlu_intent_ids:
                print("WARNING: no NLU data for intent",intent + "_" + language.lower())

    print("nlu.md written.")


    # ### stories.md

    # In[127]:

    def write_default_story(intent_topic, language, f):

        intent_full_id = '{intent_topic}_{language}'.format(intent_topic=intent_topic, language=language.lower())
        story_title = 'answer_{intent_full_id}'.format(intent_full_id=intent_full_id)

        # For counting
        story_ids.append(story_title)

        f.write('## {story_title}\n'.format(story_title=story_title))
        f.write('* {intent_full_id}\n'.format(intent_full_id=intent_full_id))

        if intent_topic.startswith('disease_'):
            form_disease_full_id = '{form_disease_name}_{language}'.format(form_disease_name=ASK_DISEASE_FORM_ID,
                                                                        language=language.lower())

            f.write(' - {form_disease_full_id}\n'.format(form_disease_full_id=form_disease_full_id))
            # Double curly braces means litteral curly braces
            f.write(' - form{{"name": "{form_disease_full_id}"}}\n'.format(form_disease_full_id=form_disease_full_id))
            f.write(' - form{"name": null}\n')
        else:
            answer_full_id = 'utter_answer_{intent_full_id}'.format(intent_full_id=intent_full_id)

            f.write(' - {answer_full_id}\n'.format(answer_full_id=answer_full_id))


        f.write(' - {form_feedback}_{language}\n'.format(form_feedback=ASK_FEEDBACK_FORM_ID,
                                                        language=language.lower()))
        f.write(' - utter_{form_anything_else}_{language}\n'.format(form_anything_else=ANYTHING_ELSE_STRING_ID,
                                                                    language=language.lower()))

        f.write('\n')
        return True

    def is_in_domain(intent_topic, intents):
        if intent_topic in intents:
            return True
        else:
            print("WARNING: Intent {intent_topic} not found in intent list".format(intent_topic=intent_topic))
            return False

    story_ids = []

    with open(STORIES_MD_FILE, 'w') as f:

        #Generic stories from Stories sheet
        for language in LANGUAGES:
            f.write('<!-- %s GENERIC -->\n\n'%language)
            for story in stories:
                story_id = 'answer_' + story + '_' + language.lower()

                story_ids.append(story_id)

                f.write('## %s\n'%story_id)

                for turn_taker, turn_action in zip(stories[story]['role_list'], stories[story]['action_list']):
                    if turn_taker.startswith(STORY_TURN_USER_PREFIX):
                        if not turn_action in intents:
                            print("WARNING: Story step %s not found in intent list"%intent)
                        f.write('* %s_%s\n'%(turn_action, language.lower()))
                    elif turn_taker.startswith(STORY_TURN_BOT_PREFIX):
                        if turn_action.startswith('action'):
                            f.write(' - %s_%s\n'%(turn_action, language.lower()))
                        elif turn_action.startswith('form'):
                            f.write(' - %s_%s\n'%(turn_action, language.lower()))
                            f.write(' - form{"name": "%s_%s"}\n'%(turn_action, language.lower()))
                            f.write(' - form{"name": null}\n')
                        else:
                            f.write(' - utter_%s_%s\n'%(turn_action, language.lower()))

                f.write('\n')


        # Auto-generated stories
        total = 0
        for language in LANGUAGES:
            n = 0
            intent_topics = list({intent_topic for intent_topic in all_nlus[language].keys() if is_in_domain(intent_topic, intents)})

            f.write('<!-- %s DISEASE -->\n\n'%language)
            disease_intents = [x for x in intent_topics if x.startswith('disease')]
            # The main use of write_default_story is its side effect, but we return True so that we can count up stories
            n += sum([write_default_story(intent_topic, language, f) for intent_topic in disease_intents])

            f.write('<!-- %s COVID -->\n\n'%language)
            covid_intents = [x for x in intent_topics if x.startswith('covid')]
            n += sum([write_default_story(intent_topic, language, f) for intent_topic in covid_intents])

            f.write('<!-- %s EBOLA -->\n\n'%language)
            ebola_intents = [x for x in intent_topics if x.startswith('ebola')]
            n += sum([write_default_story(intent_topic, language, f) for intent_topic in ebola_intents])

            print("{language}: {n} stories collected".format(language=language, n=n))
            total += n

        print("Total: {n} stories collected".format(n=n))

        #Check if all intents are covered by a story
        for language in LANGUAGES:
            for intent in intents:
                story_id = 'answer_' + intent + '_' + language.lower()
                if not story_id in story_ids:
                    print("WARNING: no story for intent",intent + "_" + language.lower())

    print("stories.md written.")


    # In[ ]:
