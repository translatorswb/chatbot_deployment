# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/

# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, Form, EventType
from rasa_sdk.forms import FormAction
from typing import Dict, Text, Any, List, Union

import json
import requests


import logging
import typing
from typing import Dict, Text, Any, List, Union, Optional, Tuple

from rasa_sdk import utils
from rasa_sdk.events import SlotSet, Form, EventType
from rasa_sdk.interfaces import Action, ActionExecutionRejection
# import spacy
# from spacy_langdetect import LanguageDetector

from rasa_sdk.events import FollowupAction

logger = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from rasa_sdk import Tracker
    from rasa_sdk.executor import CollectingDispatcher

from fasttext import load_model
from nltk import word_tokenize
import time


# Suppress warning; it is safe to remove if you do not print
import fasttext
fasttext.FastText.eprint = lambda x: None

model = load_model("/app/en_ha_kr_model_lowered_tok_unigram_v1_20210228.ftz")


# SlotSet('feedback_hau',None)

def get_stats(dispatcher, lang):
    # this is where to paste the call to API
    country = "DRC"
    url = "https://covid-193.p.rapidapi.com/statistics"
    headers = { 'x-rapidapi-host': "covid-193.p.rapidapi.com", 'x-rapidapi-key': "c41cd0c62dmshb99d2fb0a63207dp1775a0jsna4f33aea1040"}
    query_string = {"country":country}

    # get the response
    response = requests.request("GET", url, headers=headers, params=query_string)
    response_JSON = response.json()

    #get the bits of the response we want
    active = response_JSON['response'][0]['cases']['active']
    new = response_JSON['response'][0]['cases']['new']
    new_deaths = response_JSON['response'][0]['deaths']['new']
    total_deaths = response_JSON['response'][0]['deaths']['total']
    recovered = response_JSON['response'][0]['cases']['recovered']

    if not new_deaths:
        new_deaths = 0
    if not new:
        new = 0

    dispatcher.utter_message(template=f"utter_get_infection_stats_{lang}",
                                active = active,
                                new = new,
                                country = country,
                                new_deaths = new_deaths,
                                total_deaths = total_deaths,
                                recovered = recovered
                                )

class FirstTimeFormHAU(FormAction):

    def name(self) -> Text:
        return "form_first_time_hau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        if tracker.get_slot("first_time_hau") == True:
            return["first_time_hau","given_name_hau","location_hau"]
        else:
            return["first_time_hau"]

    def slot_mappings(self) -> Text:
        return {
        "first_time_hau": [
            self.from_intent(intent="affirm_hau", value=True),
            self.from_intent(intent="deny_hau", value=False)
            ],
        "given_name_hau": self.from_text(),
        "location_hau": self.from_text()
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        if tracker.get_slot("first_time_hau") == False:
            dispatcher.utter_message(template="utter_welcome_back_hau")
        else:
#            dispatcher.utter_message(template="utter_greet")
            dispatcher.utter_message(template="utter_greet_with_name_hau")
        return[]

class FirstTimeFormKAU(FormAction):

    def name(self) -> Text:
        return "form_first_time_kau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        if tracker.get_slot("first_time_kau") == True:
            return["first_time_kau","given_name_kau","location_kau"]
        else:
            return["first_time_kau"]

    def slot_mappings(self) -> Text:
        return {
        "first_time_kau": [
            self.from_intent(intent="affirm_kau", value=True),
            self.from_intent(intent="deny_kau", value=False)
            ],
        "given_name_kau": self.from_text(),
        "location_kau": self.from_text()
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        if tracker.get_slot("first_time_kau") == False:
            dispatcher.utter_message(template="utter_welcome_back_kau")
        else:
#            dispatcher.utter_message(template="utter_greet")
            dispatcher.utter_message(template="utter_greet_with_name_kau")
        return[]

class FirstTimeFormSHU(FormAction):

    def name(self) -> Text:
        return "form_first_time_shu"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        if tracker.get_slot("first_time_shu") == True:
            return["first_time_shu","given_name_shu","location_shu"]
        else:
            return["first_time_shu"]

    def slot_mappings(self) -> Text:
        return {
        "first_time_shu": [
            self.from_intent(intent="affirm_shu", value=True),
            self.from_intent(intent="deny_shu", value=False)
            ],
        "given_name_shu": self.from_text(),
        "location_shu": self.from_text()
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        if tracker.get_slot("first_time_shu") == False:
            dispatcher.utter_message(template="utter_welcome_back_shu")
        else:
#            dispatcher.utter_message(template="utter_greet")
            dispatcher.utter_message(template="utter_greet_with_name_shu")
        return[]


class FirstTimeFormENG(FormAction):

    def name(self) -> Text:
        return "form_first_time_eng"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        if tracker.get_slot("first_time_eng") == True:
            return["first_time_shu","given_name_shu","location_shu"]
        else:
            return["first_time_shu"]

    def slot_mappings(self) -> Text:
        return {
        "first_time_eng": [
            self.from_intent(intent="affirm_shu", value=True),
            self.from_intent(intent="deny_shu", value=False)
            ],
        "given_name_eng": self.from_text(),
        "location_eng": self.from_text()
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        if tracker.get_slot("first_time_eng") == False:
            dispatcher.utter_message(template="utter_welcome_back_eng")
        else:
#            dispatcher.utter_message(template="utter_greet")
            dispatcher.utter_message(template="utter_greet_with_name_eng")
        return[]

class FeedbackFormKAU(FormAction):

    def name(self) -> Text:
        return "form_feedback_kau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        # if the answer to "Did we do OK?" is no...
        if tracker.get_slot("feedback_kau") == False:
            return["feedback_kau", "feedback_reason_kau"]
        else:
            return["feedback_kau"]

    def slot_mappings(self) -> Text:

        return {
        "feedback_kau": [
            self.from_intent(intent="affirm_kau", value=True),
            self.from_intent(intent="deny_kau", value=False)
            ],
        "feedback_reason_kau": self.from_text()
        }



    

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        if tracker.get_slot('feedback_kau'):
            return [FollowupAction('form_community_impact_kau')]
        else:
            if tracker.get_slot('feedback_reason_kau'):
                dispatcher.utter_message(template="utter_thanks_for_your_feedback_kau")
                return[SlotSet('feedback_kau',None), SlotSet('feedback_reason_kau',None)]

            dispatcher.utter_message(template='utter_ask_feedback_reason_kau')
            # return [FollowupAction('form_feedback_reason_kau')]

        
        return[SlotSet('feedback_kau',None), SlotSet('feedback_reason_kau',None)]

class FeedbackFormHAU(FormAction):

    def name(self) -> Text:
        return "form_feedback_hau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        # if the answer to "Did we do OK?" is no...
        if tracker.get_slot("feedback_hau") == False:
            return["feedback_hau", "feedback_reason_hau"]
        else:
            return["feedback_hau"]

    def slot_mappings(self) -> Text:

        return {
        "feedback_hau": [
            self.from_intent(intent="affirm_hau", value=True),
            self.from_intent(intent="deny_hau", value=False)
            ],
        "feedback_reason_hau": self.from_text()
        }



    

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        if tracker.get_slot('feedback_hau'):
            return [FollowupAction('form_community_impact_hau')]
        else:
            if tracker.get_slot('feedback_reason_hau'):
                dispatcher.utter_message(template="utter_thanks_for_your_feedback_hau")
                return[SlotSet('feedback_hau',None), SlotSet('feedback_reason_hau',None)]

            dispatcher.utter_message(template='utter_ask_feedback_reason_hau')
            # return [FollowupAction('form_feedback_reason_hau')]

        
        return[SlotSet('feedback_hau',None), SlotSet('feedback_reason_hau',None)]




class FeedbackFormENG(FormAction):

    def name(self) -> Text:
        return "form_feedback_eng"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        # if the answer to "Did we do OK?" is no...
        if tracker.get_slot("feedback_eng") == False:
            return["feedback_eng", "feedback_reason_eng"]
        else:
            return["feedback_eng"]

    def slot_mappings(self) -> Text:

        return {
        "feedback_eng": [
            self.from_intent(intent="affirm_eng", value=True),
            self.from_intent(intent="deny_eng", value=False)
            ],
        "feedback_reason_eng": self.from_text()
        }



    

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        if tracker.get_slot('feedback_eng'):
            return [FollowupAction('form_community_impact_eng')]
        else:
            if tracker.get_slot('feedback_reason_eng'):
                dispatcher.utter_message(template="utter_thanks_for_your_feedback_eng")
                return[SlotSet('feedback_eng',None), SlotSet('feedback_reason_eng',None)]

            dispatcher.utter_message(template='utter_ask_feedback_reason_eng')
            # return [FollowupAction('form_feedback_reason_eng')]

        
        return[SlotSet('feedback_eng',None), SlotSet('feedback_reason_eng',None)]


class LanguageQuestionsFormHAU(FormAction):

    def name(self) -> Text:
        return "form_language_questions_hau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        return["language_at_home_hau"]

    def slot_mappings(self) -> Text:
        return {
        "language_at_home_hau": self.from_text()
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        dispatcher.utter_message(template="utter_get_back_on_topic_hau")
        return[]

class LanguageQuestionsFormKAU(FormAction):

    def name(self) -> Text:
        return "form_language_questions_kau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        return["language_at_home_kau"]

    def slot_mappings(self) -> Text:
        return {
        "language_at_home_kau": self.from_text()
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        dispatcher.utter_message(template="utter_get_back_on_topic_kau")
        return[]

class LanguageQuestionsFormSHU(FormAction):

    def name(self) -> Text:
        return "form_language_questions_shu"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        return["language_at_home_shu"]

    def slot_mappings(self) -> Text:
        return {
        "language_at_home_shu": self.from_text()
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        dispatcher.utter_message(template="utter_get_back_on_topic_shu")
        return[]

class MythSourceFormHAU(FormAction):

    def name(self) -> Text:
        return "form_myth_source_hau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        return["myth_source_hau"]

    def slot_mappings(self) -> Text:
        return {
        "myth_source_hau": self.from_text()
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        dispatcher.utter_message(template="utter_thanks_for_your_feedback_hau")
        return[]

class MythSourceFormKAU(FormAction):

    def name(self) -> Text:
        return "form_myth_source_kau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        return["myth_source_kau"]

    def slot_mappings(self) -> Text:
        return {
        "myth_source_kau": self.from_text()
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        dispatcher.utter_message(template="utter_thanks_for_your_feedback_kau")
        return[]

class MythSourceFormSHU(FormAction):

    def name(self) -> Text:
        return "form_myth_source_shu"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        return["myth_source_shu"]

    def slot_mappings(self) -> Text:
        return {
        "myth_source_shu": self.from_text()
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        dispatcher.utter_message(template="utter_thanks_for_your_feedback_shu")
        return[]


class ActionGetInfectionStatsHAU(Action):

    def name(self) -> Text:
        return "action_get_infection_stats_hau"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # this is where to paste the call to API
        url = "https://covidnigeria.herokuapp.com/api"
        state = "Lagos"
        # get the response
        response = requests.request("GET", url)
        response_JSON = response.json()
        print(response_JSON['data']['states']['state'==state])
        #get the bits of the response we want
        total = response_JSON['data']["totalConfirmedCases"]
        active = response_JSON['data']["totalActiveCases"]
        discharged = response_JSON['data']["discharged"]
        deaths = response_JSON['data']["death"]

        dispatcher.utter_message(template="utter_get_infection_stats_hau",
                                 total = total,
                                 active = active,
                                 discharged = discharged,
                                 deaths = deaths
                                 )

        return []
        
class ActionGetInfectionStatsKAU(Action):

    def name(self) -> Text:
        return "action_get_infection_stats_kau"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # this is where to paste the call to API
        url = "https://covidnigeria.herokuapp.com/api"
        state = "Lagos"
        # get the response
        response = requests.request("GET", url)
        response_JSON = response.json()
        print(response_JSON['data']['states']['state'==state])
        #get the bits of the response we want
        total = response_JSON['data']["totalConfirmedCases"]
        active = response_JSON['data']["totalActiveCases"]
        discharged = response_JSON['data']["discharged"]
        deaths = response_JSON['data']["death"]

        dispatcher.utter_message(template="utter_get_infection_stats_kau",
                                 total = total,
                                 active = active,
                                 discharged = discharged,
                                 deaths = deaths
                                 )

        return []
        
class ActionGetInfectionStatsSHU(Action):

    def name(self) -> Text:
        return "action_get_infection_stats_shu"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # this is where to paste the call to API
        url = "https://covidnigeria.herokuapp.com/api"
        state = "Lagos"
        # get the response
        response = requests.request("GET", url)
        response_JSON = response.json()
        print(response_JSON['data']['states']['state'==state])
        #get the bits of the response we want
        total = response_JSON['data']["totalConfirmedCases"]
        active = response_JSON['data']["totalActiveCases"]
        discharged = response_JSON['data']["discharged"]
        deaths = response_JSON['data']["death"]

        dispatcher.utter_message(template="utter_get_infection_stats_shu",
                                 total = total,
                                 active = active,
                                 discharged = discharged,
                                 deaths = deaths
                                 )

        return []


class ActionGetInfectionStatsENG(Action):

    def name(self) -> Text:
        return "action_get_infection_stats_eng"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # this is where to paste the call to API
        url = "https://covidnigeria.herokuapp.com/api"
        state = "Lagos"
        # get the response
        response = requests.request("GET", url)
        response_JSON = response.json()
        print(response_JSON['data']['states']['state'==state])
        #get the bits of the response we want
        total = response_JSON['data']["totalConfirmedCases"]
        active = response_JSON['data']["totalActiveCases"]
        discharged = response_JSON['data']["discharged"]
        deaths = response_JSON['data']["death"]

        dispatcher.utter_message(template="utter_get_infection_stats_eng",
                                 total = total,
                                 active = active,
                                 discharged = discharged,
                                 deaths = deaths
                                 )

        return []

class ActionGetPandemicVideo(Action):

    def name(self) -> Text:
        return "action_shuk_to_pandemic_video"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        country = "DRC"

        # dispatcher.utter_message(attachment={
        #     "type": "video",
        #     "payload": {
        #         "title": "Watch Below Video",
        #         "src": "https://www.youtube.com/watch?v=nMelwUuGqpA"
        #     }
        # })

        return []


class LanguageQuestionsFormENG(FormAction):

    def name(self) -> Text:
        return "form_language_questions_eng"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        return["language_at_home_eng"]

    def slot_mappings(self) -> Text:
        return {
        "language_at_home_eng": self.from_text()
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        dispatcher.utter_message(template="utter_get_back_on_topic_eng")
        return[]


class MythSourceFormENG(FormAction):

    def name(self) -> Text:
        return "form_myth_source_eng"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        return["myth_source_eng"]

    def slot_mappings(self) -> Text:
        return {
        "myth_source_eng": self.from_text()
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        dispatcher.utter_message(template="utter_thanks_for_your_feedback_new_survey_eng")
        return[]


class FeedbackFormReturnUserENG(FormAction):

    def name(self) -> Text:
        return "form_feedback_return_user_eng"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        # if the answer to "Did we do OK?" is no...
        if tracker.get_slot("feedback_return_user_eng") == False:
            return ["feedback_return_user_eng", "feedback_reason_return_user_eng"]
        else:
            return ["feedback_return_user_eng"]

    def slot_mappings(self) -> Text:

        return {
            "feedback_return_user_eng": [
                self.from_intent(intent="affirm_eng", value=True),
                self.from_intent(intent="deny_eng", value=False)
            ],
            "feedback_reason_return_user_eng": self.from_text()
        }

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:

        if tracker.get_slot('feedback_return_user_eng'):
            print('Channel =========== ')
            print(tracker.get_latest_input_channel())
            if tracker.get_latest_input_channel() == "Telegram":
                dic = domain['responses']['utter_promo_link_telegram_eng'][0]
                dic['parse_mode'] = 'markdown'
                dispatcher.utter_custom_json(dic)
                dispatcher.utter_message(template="utter_promo_link_telegram_eng")
            elif tracker.get_latest_input_channel() == "Whatsapp":
                dispatcher.utter_message(template="utter_promo_link_whatsapp_eng")
            else:
                dic = domain['responses']['utter_promo_link_telegram_eng'][0]
                dic['parse_mode'] = 'markdown'
                dispatcher.utter_custom_json(dic)

                # dispatcher.utter_message(template="utter_promo_link_telegram_eng", parse_mode="markdown")
            #input_channel = tracker.events[1]['input_channel']
            #dispatcher.utter_message(input_channel)
            #return [FollowupAction('form_community_impact_eng')]
            
        else:
            if tracker.get_slot('feedback_reason_return_user_eng'):
                dispatcher.utter_message(template="utter_thanks_for_your_feedback_eng")
                return [SlotSet('feedback_return_user_eng', None), SlotSet('feedback_reason_return_user_eng', tracker.get_slot('feedback_reason_return_user_eng'))]
            
            # dispatcher.utter_message(template='utter_ask_feedback_reason_return_user_eng')
            #return [FollowupAction('form_feedback_reason_return_user_eng')]
        return [SlotSet('feedback_return_user_eng', None), SlotSet('feedback_reason_return_user_eng', None)]


class CommunityImpactFormENG(FormAction):

    def name(self) -> Text:
        return "form_community_impact_eng"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return["community_impact_eng"]
            

    def slot_mappings(self) -> Text:
        return {
        "community_impact_eng": [
            self.from_intent(intent="affirm_eng", value=True),
            self.from_intent(intent="deny_eng", value=False),
            self.from_intent(intent="maybe_eng", value=False)
            ]
        #"community_impact_eng": self.from_text()
        }



    

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        if tracker.get_slot('community_impact_eng'):
            return [FollowupAction('form_gender_question_a_eng'), SlotSet('community_impact_eng', tracker.get_slot('community_impact_eng'))]

        else:
            return [FollowupAction('form_gender_question_b_eng'), SlotSet('community_impact_eng', tracker.get_slot('community_impact_eng'))]

        # import pdb; pdb.set_trace()

        return[SlotSet('community_impact_eng',None)]




class GenderQuestionAFormENG(FormAction):

    def name(self) -> Text:
        return "form_gender_question_a_eng"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return["gender_question_a_eng"]
            

    def slot_mappings(self) -> Text:
        #import pdb; pdb.set_trace()
        return {
        "gender_question_a_eng": [
            self.from_intent(intent="gender_male_eng", value="Male"),
            self.from_intent(intent="gender_female_eng", value="Female"),
            self.from_intent(intent="prefer_not_to_answer_eng", value="Prefer not to answer")
            ]
        #"gender_question_a_eng": self.from_text()
        }



    

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        # if tracker.get_slot('community_impact_eng'):
        #     dispatcher.utter_message(template='utter_community_impact_survey_eng')

        # else:
        #     dispatcher.utter_message(template='utter_ask_feedback_reason_eng')

        # import pdb; pdb.set_trace()
        if not tracker.get_slot('gender_question_a_eng') is None:
            dispatcher.utter_message(template="utter_thanks_for_your_feedback_new_survey_eng")
            #dispatcher.utter_message(template="utter_anything_else_eng")

        return[SlotSet('gender_question_a_eng',tracker.get_slot('gender_question_a_eng'))]


class GenderQuestionBFormENG(FormAction):

    def name(self) -> Text:
        return "form_gender_question_b_eng"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return["gender_question_b_eng"]
            

    def slot_mappings(self) -> Text:
        return {
        "gender_question_b_eng": [
            self.from_intent(intent="gender_male_eng", value="Male"),
            self.from_intent(intent="gender_female_eng", value="Female"),
            self.from_intent(intent="prefer_not_to_answer_eng", value="Prefer not to answer")
            ]
        #"gender_question_b_eng": self.from_text()
        }



    

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        # if tracker.get_slot('community_impact_eng'):
        #     dispatcher.utter_message(template='utter_community_impact_survey_eng')

        # else:
        #     dispatcher.utter_message(template='utter_ask_feedback_reason_eng')

        # import pdb; pdb.set_trace()
        if not tracker.get_slot('gender_question_b_eng') is None:
            dispatcher.utter_message(template="utter_thanks_for_your_feedback_new_survey_eng")
            #dispatcher.utter_message(template="utter_anything_else_eng")

        return[SlotSet('gender_question_b_eng',tracker.get_slot('gender_question_b_eng'))]


class ActionGetFAQCtrENG(Action):

    def name(self) -> Text:
        return "action_get_faq_ctr_eng"

    

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        print(tracker.slots)

        events = tracker.current_state()['events']
        user_events = [i for i in events if i['event'] == 'user']
        
        feedback_ctr = tracker.get_slot('feedback_ctr_eng')
        if feedback_ctr is None:
            feedback_ctr = 0

        feedback_ctr += 1

        print('========================',feedback_ctr)


        # if (feedback_ctr % 3) == 0:
        if (feedback_ctr == 3):
            # pro = FeedbackFormKAU()
            # await pro.run(dispatcher,tracker,domain)
            # # dispatcher.utter_message(template=f"utter_out_of_scope_hau")
            
            # tracker.trigger_follow_up_action('form_feedback_kau')
            # feedback_ctr = 0

            # FollowupAction('form_feedback_eng')
            time.sleep(1)
            # return [FollowupAction('form_feedback_eng'), SlotSet('feedback_ctr_eng',feedback_ctr)]
            return [FollowupAction('form_quiz_eng'), SlotSet('feedback_ctr_eng', feedback_ctr)]

        elif (feedback_ctr == 6):
            time.sleep(1)
            return [FollowupAction('form_feedback_return_user_eng'), SlotSet('feedback_ctr_eng', feedback_ctr)]
        
        
        # user_event_count = len(user_events)
        time.sleep(1)
        return [SlotSet('feedback_ctr_eng',feedback_ctr)]





class ActionGetPandemicVideo(Action):

    def name(self) -> Text:
        return "action_shuk_to_pandemic_video"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        country = "DRC"

        # dispatcher.utter_message(attachment={
        #     "type": "video",
        #     "payload": {
        #         "title": "Watch Below Video",
        #         "src": "https://www.youtube.com/watch?v=nMelwUuGqpA"
        #     }
        # })

        return []


class LanguageQuestionsFormHAU(FormAction):

    def name(self) -> Text:
        return "form_language_questions_hau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        return["language_at_home_hau"]

    def slot_mappings(self) -> Text:
        return {
        "language_at_home_hau": self.from_text()
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        dispatcher.utter_message(template="utter_get_back_on_topic_hau")
        return[]


class MythSourceFormHAU(FormAction):

    def name(self) -> Text:
        return "form_myth_source_hau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        return["myth_source_hau"]

    def slot_mappings(self) -> Text:
        return {
        "myth_source_hau": self.from_text()
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        dispatcher.utter_message(template="utter_thanks_for_your_feedback_new_survey_hau")
        return[]


class FeedbackFormReturnUserHAU(FormAction):

    def name(self) -> Text:
        return "form_feedback_return_user_hau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        # if the answer to "Did we do OK?" is no...
        if tracker.get_slot("feedback_return_user_hau") == False:
            return ["feedback_return_user_hau", "feedback_reason_return_user_hau"]
        else:
            return ["feedback_return_user_hau"]

    def slot_mappings(self) -> Text:

        return {
            "feedback_return_user_hau": [
                self.from_intent(intent="affirm_hau", value=True),
                self.from_intent(intent="deny_hau", value=False)
            ],
            "feedback_reason_return_user_hau": self.from_text()
        }

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:

        if tracker.get_slot('feedback_return_user_hau'):
            print('Channel =========== ')
            print(tracker.get_latest_input_channel())
            if tracker.get_latest_input_channel() == "Telegram":
                dic = domain['responses']['utter_promo_link_telegram_hau'][0]
                dic['parse_mode'] = 'markdown'
                dispatcher.utter_custom_json(dic)
                dispatcher.utter_message(template="utter_promo_link_telegram_hau")
            elif tracker.get_latest_input_channel() == "Whatsapp":
                dispatcher.utter_message(template="utter_promo_link_whatsapp_hau")
            else:
                dic = domain['responses']['utter_promo_link_telegram_hau'][0]
                dic['parse_mode'] = 'markdown'
                dispatcher.utter_custom_json(dic)

                # dispatcher.utter_message(template="utter_promo_link_telegram_hau", parse_mode="markdown")
            #input_channel = tracker.events[1]['input_channel']
            #dispatcher.utter_message(input_channel)
            #return [FollowupAction('form_community_impact_hau')]
            
        else:
            if tracker.get_slot('feedback_reason_return_user_hau'):
                dispatcher.utter_message(template="utter_thanks_for_your_feedback_hau")
                return [SlotSet('feedback_return_user_hau', None), SlotSet('feedback_reason_return_user_hau', tracker.get_slot('feedback_reason_return_user_hau'))]
            
            # dispatcher.utter_message(template='utter_ask_feedback_reason_return_user_hau')
            #return [FollowupAction('form_feedback_reason_return_user_hau')]
        return [SlotSet('feedback_return_user_hau', None), SlotSet('feedback_reason_return_user_hau', None)]


class CommunityImpactFormHAU(FormAction):

    def name(self) -> Text:
        return "form_community_impact_hau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return["community_impact_hau"]
            

    def slot_mappings(self) -> Text:
        return {
        "community_impact_hau": [
            self.from_intent(intent="affirm_hau", value=True),
            self.from_intent(intent="deny_hau", value=False),
            self.from_intent(intent="maybe_hau", value=False)
            ]
        #"community_impact_hau": self.from_text()
        }



    

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        if tracker.get_slot('community_impact_hau'):
            return [FollowupAction('form_gender_question_a_hau'), SlotSet('community_impact_hau', tracker.get_slot('community_impact_hau'))]

        else:
            return [FollowupAction('form_gender_question_b_hau'), SlotSet('community_impact_hau', tracker.get_slot('community_impact_hau'))]

        # import pdb; pdb.set_trace()

        return[SlotSet('community_impact_hau',None)]




class GenderQuestionAFormHAU(FormAction):

    def name(self) -> Text:
        return "form_gender_question_a_hau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return["gender_question_a_hau"]
            

    def slot_mappings(self) -> Text:
        #import pdb; pdb.set_trace()
        return {
        "gender_question_a_hau": [
            self.from_intent(intent="gender_male_hau", value="Male"),
            self.from_intent(intent="gender_female_hau", value="Female"),
            self.from_intent(intent="prefer_not_to_answer_hau", value="Prefer not to answer")
            ]
        #"gender_question_a_hau": self.from_text()
        }



    

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        # if tracker.get_slot('community_impact_hau'):
        #     dispatcher.utter_message(template='utter_community_impact_survey_hau')

        # else:
        #     dispatcher.utter_message(template='utter_ask_feedback_reason_hau')

        # import pdb; pdb.set_trace()
        if not tracker.get_slot('gender_question_a_hau') is None:
            dispatcher.utter_message(template="utter_thanks_for_your_feedback_new_survey_hau")
            #dispatcher.utter_message(template="utter_anything_else_hau")

        return[SlotSet('gender_question_a_hau',tracker.get_slot('gender_question_a_hau'))]


class GenderQuestionBFormHAU(FormAction):

    def name(self) -> Text:
        return "form_gender_question_b_hau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return["gender_question_b_hau"]
            

    def slot_mappings(self) -> Text:
        return {
        "gender_question_b_hau": [
            self.from_intent(intent="gender_male_hau", value="Male"),
            self.from_intent(intent="gender_female_hau", value="Female"),
            self.from_intent(intent="prefer_not_to_answer_hau", value="Prefer not to answer")
            ]
        #"gender_question_b_hau": self.from_text()
        }



    

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        # if tracker.get_slot('community_impact_hau'):
        #     dispatcher.utter_message(template='utter_community_impact_survey_hau')

        # else:
        #     dispatcher.utter_message(template='utter_ask_feedback_reason_hau')

        # import pdb; pdb.set_trace()
        if not tracker.get_slot('gender_question_b_hau') is None:
            dispatcher.utter_message(template="utter_thanks_for_your_feedback_new_survey_hau")
            #dispatcher.utter_message(template="utter_anything_else_hau")

        return[SlotSet('gender_question_b_hau',tracker.get_slot('gender_question_b_hau'))]


class ActionGetFAQCtrHAU(Action):

    def name(self) -> Text:
        return "action_get_faq_ctr_hau"

    

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        print(tracker.slots)

        events = tracker.current_state()['events']
        user_events = [i for i in events if i['event'] == 'user']
        
        feedback_ctr = tracker.get_slot('feedback_ctr_hau')
        if feedback_ctr is None:
            feedback_ctr = 0

        feedback_ctr += 1

        print('========================',feedback_ctr)


        # if (feedback_ctr % 3) == 0:
        if (feedback_ctr == 3):
            # pro = FeedbackFormKAU()
            # await pro.run(dispatcher,tracker,domain)
            # # dispatcher.utter_message(template=f"utter_out_of_scope_hau")
            
            # tracker.trigger_follow_up_action('form_feedback_kau')
            # feedback_ctr = 0

            # FollowupAction('form_feedback_hau')
            time.sleep(1)
            # return [FollowupAction('form_feedback_hau'), SlotSet('feedback_ctr_hau',feedback_ctr)]
            return [FollowupAction('form_quiz_hau'), SlotSet('feedback_ctr_hau', feedback_ctr)]


        elif (feedback_ctr == 6):
            time.sleep(1)
            return [FollowupAction('form_feedback_return_user_hau'), SlotSet('feedback_ctr_hau', feedback_ctr)]
        
        
        # user_event_count = len(user_events)
        time.sleep(1)
        return [SlotSet('feedback_ctr_hau',feedback_ctr)]




class ActionGetPandemicVideo(Action):

    def name(self) -> Text:
        return "action_shuk_to_pandemic_video"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        country = "DRC"

        # dispatcher.utter_message(attachment={
        #     "type": "video",
        #     "payload": {
        #         "title": "Watch Below Video",
        #         "src": "https://www.youtube.com/watch?v=nMelwUuGqpA"
        #     }
        # })

        return []


class LanguageQuestionsFormKAU(FormAction):

    def name(self) -> Text:
        return "form_language_questions_kau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        return["language_at_home_kau"]

    def slot_mappings(self) -> Text:
        return {
        "language_at_home_kau": self.from_text()
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        dispatcher.utter_message(template="utter_get_back_on_topic_kau")
        return[]


class MythSourceFormKAU(FormAction):

    def name(self) -> Text:
        return "form_myth_source_kau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        return["myth_source_kau"]

    def slot_mappings(self) -> Text:
        return {
        "myth_source_kau": self.from_text()
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        dispatcher.utter_message(template="utter_thanks_for_your_feedback_new_survey_kau")
        return[]


class FeedbackFormReturnUserKAU(FormAction):

    def name(self) -> Text:
        return "form_feedback_return_user_kau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        # if the answer to "Did we do OK?" is no...
        if tracker.get_slot("feedback_return_user_kau") == False:
            return ["feedback_return_user_kau", "feedback_reason_return_user_kau"]
        else:
            return ["feedback_return_user_kau"]

    def slot_mappings(self) -> Text:

        return {
            "feedback_return_user_kau": [
                self.from_intent(intent="affirm_kau", value=True),
                self.from_intent(intent="deny_kau", value=False)
            ],
            "feedback_reason_return_user_kau": self.from_text()
        }

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:

        if tracker.get_slot('feedback_return_user_kau'):
            print('Channel =========== ')
            print(tracker.get_latest_input_channel())
            if tracker.get_latest_input_channel() == "Telegram":
                dic = domain['responses']['utter_promo_link_telegram_kau'][0]
                dic['parse_mode'] = 'markdown'
                dispatcher.utter_custom_json(dic)
                dispatcher.utter_message(template="utter_promo_link_telegram_kau")
            elif tracker.get_latest_input_channel() == "Whatsapp":
                dispatcher.utter_message(template="utter_promo_link_whatsapp_kau")
            else:
                dic = domain['responses']['utter_promo_link_telegram_kau'][0]
                dic['parse_mode'] = 'markdown'
                dispatcher.utter_custom_json(dic)

                # dispatcher.utter_message(template="utter_promo_link_telegram_kau", parse_mode="markdown")
            #input_channel = tracker.events[1]['input_channel']
            #dispatcher.utter_message(input_channel)
            #return [FollowupAction('form_community_impact_kau')]
            
        else:
            if tracker.get_slot('feedback_reason_return_user_kau'):
                dispatcher.utter_message(template="utter_thanks_for_your_feedback_kau")
                return [SlotSet('feedback_return_user_kau', None), SlotSet('feedback_reason_return_user_kau', tracker.get_slot('feedback_reason_return_user_kau'))]
            
            # dispatcher.utter_message(template='utter_ask_feedback_reason_return_user_kau')
            #return [FollowupAction('form_feedback_reason_return_user_kau')]
        return [SlotSet('feedback_return_user_kau', None), SlotSet('feedback_reason_return_user_kau', None)]


class CommunityImpactFormKAU(FormAction):

    def name(self) -> Text:
        return "form_community_impact_kau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return["community_impact_kau"]
            

    def slot_mappings(self) -> Text:
        return {
        "community_impact_kau": [
            self.from_intent(intent="affirm_kau", value=True),
            self.from_intent(intent="deny_kau", value=False),
            self.from_intent(intent="maybe_kau", value=False)
            ]
        #"community_impact_kau": self.from_text()
        }



    

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        if tracker.get_slot('community_impact_kau'):
            return [FollowupAction('form_gender_question_a_kau'), SlotSet('community_impact_kau', tracker.get_slot('community_impact_kau'))]

        else:
            return [FollowupAction('form_gender_question_b_kau'), SlotSet('community_impact_kau', tracker.get_slot('community_impact_kau'))]

        # import pdb; pdb.set_trace()

        return[SlotSet('community_impact_kau',None)]




class GenderQuestionAFormKAU(FormAction):

    def name(self) -> Text:
        return "form_gender_question_a_kau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return["gender_question_a_kau"]
            

    def slot_mappings(self) -> Text:
        #import pdb; pdb.set_trace()
        return {
        "gender_question_a_kau": [
            self.from_intent(intent="gender_male_kau", value="Male"),
            self.from_intent(intent="gender_female_kau", value="Female"),
            self.from_intent(intent="prefer_not_to_answer_kau", value="Prefer not to answer")
            ]
        #"gender_question_a_kau": self.from_text()
        }



    

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        # if tracker.get_slot('community_impact_kau'):
        #     dispatcher.utter_message(template='utter_community_impact_survey_kau')

        # else:
        #     dispatcher.utter_message(template='utter_ask_feedback_reason_kau')

        # import pdb; pdb.set_trace()
        if not tracker.get_slot('gender_question_a_kau') is None:
            dispatcher.utter_message(template="utter_thanks_for_your_feedback_new_survey_kau")
            #dispatcher.utter_message(template="utter_anything_else_kau")

        return[SlotSet('gender_question_a_kau',tracker.get_slot('gender_question_a_kau'))]


class GenderQuestionBFormKAU(FormAction):

    def name(self) -> Text:
        return "form_gender_question_b_kau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return["gender_question_b_kau"]
            

    def slot_mappings(self) -> Text:
        return {
        "gender_question_b_kau": [
            self.from_intent(intent="gender_male_kau", value="Male"),
            self.from_intent(intent="gender_female_kau", value="Female"),
            self.from_intent(intent="prefer_not_to_answer_kau", value="Prefer not to answer")
            ]
        #"gender_question_b_kau": self.from_text()
        }



    

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        # if tracker.get_slot('community_impact_kau'):
        #     dispatcher.utter_message(template='utter_community_impact_survey_kau')

        # else:
        #     dispatcher.utter_message(template='utter_ask_feedback_reason_kau')

        # import pdb; pdb.set_trace()
        if not tracker.get_slot('gender_question_b_kau') is None:
            dispatcher.utter_message(template="utter_thanks_for_your_feedback_new_survey_kau")
            #dispatcher.utter_message(template="utter_anything_else_kau")

        return[SlotSet('gender_question_b_kau',tracker.get_slot('gender_question_b_kau'))]


class ActionGetFAQCtrKAU(Action):

    def name(self) -> Text:
        return "action_get_faq_ctr_kau"

    

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        print(tracker.slots)

        events = tracker.current_state()['events']
        user_events = [i for i in events if i['event'] == 'user']
        
        feedback_ctr = tracker.get_slot('feedback_ctr_kau')
        if feedback_ctr is None:
            feedback_ctr = 0

        feedback_ctr += 1

        print('========================',feedback_ctr)


        # if (feedback_ctr % 3) == 0:
        if (feedback_ctr == 3):
            # pro = FeedbackFormKAU()
            # await pro.run(dispatcher,tracker,domain)
            # # dispatcher.utter_message(template=f"utter_out_of_scope_kau")
            
            # tracker.trigger_follow_up_action('form_feedback_kau')
            # feedback_ctr = 0

            # FollowupAction('form_feedback_kau')
            time.sleep(1)
            # return [FollowupAction('form_feedback_kau'), SlotSet('feedback_ctr_kau',feedback_ctr)]
            return [FollowupAction('form_quiz_kau'), SlotSet('feedback_ctr_kau', feedback_ctr)]

        elif (feedback_ctr == 6):
            time.sleep(1)
            return [FollowupAction('form_feedback_return_user_kau'), SlotSet('feedback_ctr_kau', feedback_ctr)]
        
        
        # user_event_count = len(user_events)
        time.sleep(1)
        return [SlotSet('feedback_ctr_kau',feedback_ctr)]




class ActionOutOfScope(Action):

    def name(self) -> Text:
        return "action_out_of_scope"

    

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        langs = {
            'ha':'hau',
            'kr': 'kau',
            'sh': 'shu',
            'en': 'eng'
        }

    
        
        text = tracker.latest_message['text']
        j = 0
        lan = None
        for i in range(len(tracker.events)-1,0,-1):
            if tracker.events[i]['event']=='user':
                if j==1:
                    if '_' in str(tracker.events[i]['parse_data']['intent']['name']):
                        lan = str(tracker.events[i]['parse_data']['intent']['name']).split('_')[-1]
                    
                    
                    break
                j+=1

        
        if lan is None:
            
            
            text = text.strip().lower()
            text = " ".join(word_tokenize(text))
            
            languages, probabilities = model.predict(text, k=3)
            lang = languages[0].replace('__label__','')

            lan = 'eng'
            if lang in langs:
                lan = langs[lang]

        
        dispatcher.utter_message(template=f"utter_out_of_scope_{lan}")


        return[]


class QuizFormHAU(FormAction):

    def name(self) -> Text:
        return "form_quiz_hau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        if not tracker.get_slot("quiz_hau"):
            return ["quiz_hau"]
        else:
            return ["quiz_hau", "quiz_level_1_question_1_hau", "quiz_level_1_question_2_hau", "quiz_level_1_question_3_hau", "quiz_level_1_question_4_hau", "quiz_level_1_question_5_hau"]

    def slot_mappings(self) -> Text:

        return {
            "quiz_hau": [
                self.from_intent(intent="affirm_hau", value=True),
                self.from_intent(intent="deny_hau", value=False)
            ],
            "quiz_level_1_question_1_hau": [
                self.from_intent(intent="affirm_hau", value=True),
                self.from_intent(intent="deny_hau", value=False)
            ],
            "quiz_level_1_question_2_hau": [
                self.from_intent(intent="affirm_hau", value=True),
                self.from_intent(intent="deny_hau", value=False)
            ],
            "quiz_level_1_question_3_hau": [
                self.from_intent(intent="affirm_hau", value=True),
                self.from_intent(intent="deny_hau", value=False)
            ],
            "quiz_level_1_question_4_hau": [
                self.from_intent(intent="affirm_hau", value=True),
                self.from_intent(intent="deny_hau", value=False)
            ],
            "quiz_level_1_question_5_hau": [
                self.from_intent(intent="affirm_hau", value=True),
                self.from_intent(intent="deny_hau", value=False)
            ]
        }

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:

        if not tracker.get_slot('quiz_hau'):
            return [FollowupAction('form_feedback_hau'), SlotSet('feedback_ctr_hau', 3)]

        if tracker.get_slot('quiz_level_1_question_5_hau') is not None:
            score = int(tracker.get_slot('quiz_level_1_question_5_hau')[0])
            values = [tracker.get_slot('quiz_level_1_question_1_hau'),tracker.get_slot('quiz_level_1_question_2_hau'),tracker.get_slot('quiz_level_1_question_3_hau'),
                      tracker.get_slot('quiz_level_1_question_4_hau'),tracker.get_slot('quiz_level_1_question_5_hau')]
            txt = ""
            for v in values:
                if v[3]=='wrong':
                    temp = f'For question {v[5]}; that was actually {v[2]} > {v[4]}'
                    txt = temp + "\n" + txt
            score_ = 5-score
            if score==5:
                dispatcher.utter_message(template="utter_score_full_hau")
            else:
                # dispatcher.utter_message(text=f"not bad your score is: correct answers: {score} wrong answers: {5-score}\n{txt}")
                dispatcher.utter_message(template="utter_score_hau", score=score, score_=score_)
                for v in values:
                    if v[3] == 'wrong':
                        dispatcher.utter_message(template="utter_score_feedback_hau", Q=v[5], A=v[2], feedback=v[4])

            return [FollowupAction('form_feedback_hau'), SlotSet('feedback_ctr_hau', 3),
                    SlotSet('quiz_hau', tracker.get_slot('quiz_hau')),
                    SlotSet('quiz_level_1_question_1_hau', None),
                    SlotSet('quiz_level_1_question_2_hau', None),
                    SlotSet('quiz_level_1_question_3_hau', None),
                    SlotSet('quiz_level_1_question_4_hau', None),
                    SlotSet('quiz_score_hau', tracker.get_slot('quiz_level_1_question_5_hau')[0]),
                    SlotSet('quiz_level_1_question_5_hau', None)]

    @staticmethod
    def quiz_level_1_question_1_hau_db() -> Dict[Text, Any]:
        with open('quiz_data.json') as f:
            data = json.load(f)
        dic = {}
        for i in range(0, len(data)):
            dic[str(data[i]['question']['HAU'])] = [data[i]['key'], str(data[i]['answer']['HAU'])]
        return dic

    def validate_quiz_level_1_question_1_hau(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        text = ''
        s = 0
        for event in tracker.events:
            if (event.get("event") == "bot") and (event.get("event") is not None):
                text = event.get("text")
        for i in self.quiz_level_1_question_1_hau_db().keys():
            if i == text:
                if value == self.quiz_level_1_question_1_hau_db()[i][0]:
                    s+=1
                    return {'quiz_level_1_question_1_hau': [s, text, str(self.quiz_level_1_question_1_hau_db()[i][0]), "correct", "feedback NA", 1]}
                else:
                    return {'quiz_level_1_question_1_hau': [s, text, str(self.quiz_level_1_question_1_hau_db()[i][0]), "wrong", str(self.quiz_level_1_question_1_hau_db()[i][1]), 1]}

    @staticmethod
    def quiz_level_1_question_2_hau_db() -> Dict[Text, Any]:
        with open('quiz_data.json') as f:
            data = json.load(f)
        dic = {}
        for i in range(0, len(data)):
            dic[str(data[i]['question']['HAU'])] = [data[i]['key'], str(data[i]['answer']['HAU'])]
        return dic

    def validate_quiz_level_1_question_2_hau(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        s = int(tracker.get_slot('quiz_level_1_question_1_hau')[0])
        text = ''
        for event in tracker.events:
            if (event.get("event") == "bot") and (event.get("event") is not None):
                text = event.get("text")
        for i in self.quiz_level_1_question_2_hau_db().keys():
            if i == text:
                if value == self.quiz_level_1_question_2_hau_db()[i][0]:
                    s+=1
                    return {'quiz_level_1_question_2_hau': [s, text, str(self.quiz_level_1_question_2_hau_db()[i][0]), "correct", "feedback NA", 2]}
                else:
                    return {'quiz_level_1_question_2_hau': [s, text, str(self.quiz_level_1_question_2_hau_db()[i][0]), "wrong", str(self.quiz_level_1_question_2_hau_db()[i][1]), 2]}


    @staticmethod
    def quiz_level_1_question_3_hau_db() -> Dict[Text, Any]:
        with open('quiz_data.json') as f:
            data = json.load(f)
        dic = {}
        for i in range(0, len(data)):
            dic[str(data[i]['question']['HAU'])] = [data[i]['key'], str(data[i]['answer']['HAU'])]
        return dic

    def validate_quiz_level_1_question_3_hau(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        s = int(tracker.get_slot('quiz_level_1_question_2_hau')[0])
        text = ''
        for event in tracker.events:
            if (event.get("event") == "bot") and (event.get("event") is not None):
                text = event.get("text")
        for i in self.quiz_level_1_question_3_hau_db().keys():
            if i == text:
                if value == self.quiz_level_1_question_3_hau_db()[i][0]:
                    s+=1
                    return {'quiz_level_1_question_3_hau': [s, text, str(self.quiz_level_1_question_3_hau_db()[i][0]), "correct", "feedback NA", 3]}
                else:
                    return {'quiz_level_1_question_3_hau': [s, text, str(self.quiz_level_1_question_3_hau_db()[i][0]), "wrong", str(self.quiz_level_1_question_3_hau_db()[i][1]), 3]}

    @staticmethod
    def quiz_level_1_question_4_hau_db() -> Dict[Text, Any]:
        with open('quiz_data.json') as f:
            data = json.load(f)
        dic = {}
        for i in range(0, len(data)):
            dic[str(data[i]['question']['HAU'])] = [data[i]['key'], str(data[i]['answer']['HAU'])]
        return dic

    def validate_quiz_level_1_question_4_hau(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        s = int(tracker.get_slot('quiz_level_1_question_3_hau')[0])
        text = ''
        for event in tracker.events:
            if (event.get("event") == "bot") and (event.get("event") is not None):
                text = event.get("text")
        for i in self.quiz_level_1_question_4_hau_db().keys():
            if i == text:
                if value == self.quiz_level_1_question_4_hau_db()[i][0]:
                    s+=1
                    return {'quiz_level_1_question_4_hau': [s, text, str(self.quiz_level_1_question_4_hau_db()[i][0]), "correct", "feedback NA", 4]}
                else:
                    return {'quiz_level_1_question_4_hau': [s, text, str(self.quiz_level_1_question_4_hau_db()[i][0]), "wrong", str(self.quiz_level_1_question_4_hau_db()[i][1]), 4]}

    @staticmethod
    def quiz_level_1_question_5_hau_db() -> Dict[Text, Any]:
        with open('quiz_data.json') as f:
            data = json.load(f)
        dic = {}
        for i in range(0, len(data)):
            dic[str(data[i]['question']['HAU'])] = [data[i]['key'], str(data[i]['answer']['HAU'])]
        return dic

    def validate_quiz_level_1_question_5_hau(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        s = int(tracker.get_slot('quiz_level_1_question_4_hau')[0])
        text = ''
        for event in tracker.events:
            if (event.get("event") == "bot") and (event.get("event") is not None):
                text = event.get("text")
        for i in self.quiz_level_1_question_5_hau_db().keys():
            if i == text:
                if value == self.quiz_level_1_question_5_hau_db()[i][0]:
                    s+=1
                    return {'quiz_level_1_question_5_hau': [s, text, str(self.quiz_level_1_question_5_hau_db()[i][0]), "correct", "feedback NA", 5]}
                else:
                    return {'quiz_level_1_question_5_hau': [s, text, str(self.quiz_level_1_question_5_hau_db()[i][0]), "wrong", str(self.quiz_level_1_question_5_hau_db()[i][1]), 5]}


class QuizFormKAU(FormAction):

    def name(self) -> Text:
        return "form_quiz_kau"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        if not tracker.get_slot("quiz_kau"):
            return ["quiz_kau"]
        else:
            return ["quiz_kau", "quiz_level_1_question_1_kau", "quiz_level_1_question_2_kau", "quiz_level_1_question_3_kau", "quiz_level_1_question_4_kau", "quiz_level_1_question_5_kau"]

    def slot_mappings(self) -> Text:

        return {
            "quiz_kau": [
                self.from_intent(intent="affirm_kau", value=True),
                self.from_intent(intent="deny_kau", value=False)
            ],
            "quiz_level_1_question_1_kau": [
                self.from_intent(intent="affirm_kau", value=True),
                self.from_intent(intent="deny_kau", value=False)
            ],
            "quiz_level_1_question_2_kau": [
                self.from_intent(intent="affirm_kau", value=True),
                self.from_intent(intent="deny_kau", value=False)
            ],
            "quiz_level_1_question_3_kau": [
                self.from_intent(intent="affirm_kau", value=True),
                self.from_intent(intent="deny_kau", value=False)
            ],
            "quiz_level_1_question_4_kau": [
                self.from_intent(intent="affirm_kau", value=True),
                self.from_intent(intent="deny_kau", value=False)
            ],
            "quiz_level_1_question_5_kau": [
                self.from_intent(intent="affirm_kau", value=True),
                self.from_intent(intent="deny_kau", value=False)
            ]
        }

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:

        if not tracker.get_slot('quiz_kau'):
            return [FollowupAction('form_feedback_kau'), SlotSet('feedback_ctr_kau', 3)]

        if tracker.get_slot('quiz_level_1_question_5_kau') is not None:
            score = int(tracker.get_slot('quiz_level_1_question_5_kau')[0])
            values = [tracker.get_slot('quiz_level_1_question_1_kau'),tracker.get_slot('quiz_level_1_question_2_kau'),tracker.get_slot('quiz_level_1_question_3_kau'),
                      tracker.get_slot('quiz_level_1_question_4_kau'),tracker.get_slot('quiz_level_1_question_5_kau')]
            txt = ""
            for v in values:
                if v[3]=='wrong':
                    temp = f'For question {v[5]}; that was actually {v[2]} > {v[4]}'
                    txt = temp + "\n" + txt
            score_ = 5-score
            if score==5:
                dispatcher.utter_message(template="utter_score_full_kau")
            else:
                # dispatcher.utter_message(text=f"not bad your score is: correct answers: {score} wrong answers: {5-score}\n{txt}")
                dispatcher.utter_message(template="utter_score_kau", score=score, score_=score_)
                for v in values:
                    if v[3] == 'wrong':
                        dispatcher.utter_message(template="utter_score_feedback_kau", Q=v[5], A=v[2], feedback=v[4])

            return [FollowupAction('form_feedback_kau'), SlotSet('feedback_ctr_kau', 3),
                    SlotSet('quiz_kau', tracker.get_slot('quiz_kau')),
                    SlotSet('quiz_level_1_question_1_kau', None),
                    SlotSet('quiz_level_1_question_2_kau', None),
                    SlotSet('quiz_level_1_question_3_kau', None),
                    SlotSet('quiz_level_1_question_4_kau', None),
                    SlotSet('quiz_score_kau', tracker.get_slot('quiz_level_1_question_5_kau')[0]),
                    SlotSet('quiz_level_1_question_5_kau', None)]

    @staticmethod
    def quiz_level_1_question_1_kau_db() -> Dict[Text, Any]:
        with open('quiz_data.json') as f:
            data = json.load(f)
        dic = {}
        for i in range(0, len(data)):
            dic[str(data[i]['question']['KAU'])] = [data[i]['key'], str(data[i]['answer']['KAU'])]
        return dic

    def validate_quiz_level_1_question_1_kau(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        text = ''
        s = 0
        for event in tracker.events:
            if (event.get("event") == "bot") and (event.get("event") is not None):
                text = event.get("text")
        for i in self.quiz_level_1_question_1_kau_db().keys():
            if i == text:
                if value == self.quiz_level_1_question_1_kau_db()[i][0]:
                    s+=1
                    return {'quiz_level_1_question_1_kau': [s, text, str(self.quiz_level_1_question_1_kau_db()[i][0]), "correct", "feedback NA", 1]}
                else:
                    return {'quiz_level_1_question_1_kau': [s, text, str(self.quiz_level_1_question_1_kau_db()[i][0]), "wrong", str(self.quiz_level_1_question_1_kau_db()[i][1]), 1]}

    @staticmethod
    def quiz_level_1_question_2_kau_db() -> Dict[Text, Any]:
        with open('quiz_data.json') as f:
            data = json.load(f)
        dic = {}
        for i in range(0, len(data)):
            dic[str(data[i]['question']['KAU'])] = [data[i]['key'], str(data[i]['answer']['KAU'])]
        return dic

    def validate_quiz_level_1_question_2_kau(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        s = int(tracker.get_slot('quiz_level_1_question_1_kau')[0])
        text = ''
        for event in tracker.events:
            if (event.get("event") == "bot") and (event.get("event") is not None):
                text = event.get("text")
        for i in self.quiz_level_1_question_2_kau_db().keys():
            if i == text:
                if value == self.quiz_level_1_question_2_kau_db()[i][0]:
                    s+=1
                    return {'quiz_level_1_question_2_kau': [s, text, str(self.quiz_level_1_question_2_kau_db()[i][0]), "correct", "feedback NA", 2]}
                else:
                    return {'quiz_level_1_question_2_kau': [s, text, str(self.quiz_level_1_question_2_kau_db()[i][0]), "wrong", str(self.quiz_level_1_question_2_kau_db()[i][1]), 2]}


    @staticmethod
    def quiz_level_1_question_3_kau_db() -> Dict[Text, Any]:
        with open('quiz_data.json') as f:
            data = json.load(f)
        dic = {}
        for i in range(0, len(data)):
            dic[str(data[i]['question']['KAU'])] = [data[i]['key'], str(data[i]['answer']['KAU'])]
        return dic

    def validate_quiz_level_1_question_3_kau(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        s = int(tracker.get_slot('quiz_level_1_question_2_kau')[0])
        text = ''
        for event in tracker.events:
            if (event.get("event") == "bot") and (event.get("event") is not None):
                text = event.get("text")
        for i in self.quiz_level_1_question_3_kau_db().keys():
            if i == text:
                if value == self.quiz_level_1_question_3_kau_db()[i][0]:
                    s+=1
                    return {'quiz_level_1_question_3_kau': [s, text, str(self.quiz_level_1_question_3_kau_db()[i][0]), "correct", "feedback NA", 3]}
                else:
                    return {'quiz_level_1_question_3_kau': [s, text, str(self.quiz_level_1_question_3_kau_db()[i][0]), "wrong", str(self.quiz_level_1_question_3_kau_db()[i][1]), 3]}

    @staticmethod
    def quiz_level_1_question_4_kau_db() -> Dict[Text, Any]:
        with open('quiz_data.json') as f:
            data = json.load(f)
        dic = {}
        for i in range(0, len(data)):
            dic[str(data[i]['question']['KAU'])] = [data[i]['key'], str(data[i]['answer']['KAU'])]
        return dic

    def validate_quiz_level_1_question_4_kau(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        s = int(tracker.get_slot('quiz_level_1_question_3_kau')[0])
        text = ''
        for event in tracker.events:
            if (event.get("event") == "bot") and (event.get("event") is not None):
                text = event.get("text")
        for i in self.quiz_level_1_question_4_kau_db().keys():
            if i == text:
                if value == self.quiz_level_1_question_4_kau_db()[i][0]:
                    s+=1
                    return {'quiz_level_1_question_4_kau': [s, text, str(self.quiz_level_1_question_4_kau_db()[i][0]), "correct", "feedback NA", 4]}
                else:
                    return {'quiz_level_1_question_4_kau': [s, text, str(self.quiz_level_1_question_4_kau_db()[i][0]), "wrong", str(self.quiz_level_1_question_4_kau_db()[i][1]), 4]}

    @staticmethod
    def quiz_level_1_question_5_kau_db() -> Dict[Text, Any]:
        with open('quiz_data.json') as f:
            data = json.load(f)
        dic = {}
        for i in range(0, len(data)):
            dic[str(data[i]['question']['KAU'])] = [data[i]['key'], str(data[i]['answer']['KAU'])]
        return dic

    def validate_quiz_level_1_question_5_kau(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        s = int(tracker.get_slot('quiz_level_1_question_4_kau')[0])
        text = ''
        for event in tracker.events:
            if (event.get("event") == "bot") and (event.get("event") is not None):
                text = event.get("text")
        for i in self.quiz_level_1_question_5_kau_db().keys():
            if i == text:
                if value == self.quiz_level_1_question_5_kau_db()[i][0]:
                    s+=1
                    return {'quiz_level_1_question_5_kau': [s, text, str(self.quiz_level_1_question_5_kau_db()[i][0]), "correct", "feedback NA", 5]}
                else:
                    return {'quiz_level_1_question_5_kau': [s, text, str(self.quiz_level_1_question_5_kau_db()[i][0]), "wrong", str(self.quiz_level_1_question_5_kau_db()[i][1]), 5]}


class QuizFormENG(FormAction):

    def name(self) -> Text:
        return "form_quiz_eng"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        if not tracker.get_slot("quiz_eng"):
            return ["quiz_eng"]
        else:
            return ["quiz_eng", "quiz_level_1_question_1_eng", "quiz_level_1_question_2_eng", "quiz_level_1_question_3_eng", "quiz_level_1_question_4_eng", "quiz_level_1_question_5_eng"]

    def slot_mappings(self) -> Text:

        return {
            "quiz_eng": [
                self.from_intent(intent="affirm_eng", value=True),
                self.from_intent(intent="deny_eng", value=False)
            ],
            "quiz_level_1_question_1_eng": [
                self.from_intent(intent="affirm_eng", value=True),
                self.from_intent(intent="deny_eng", value=False)
            ],
            "quiz_level_1_question_2_eng": [
                self.from_intent(intent="affirm_eng", value=True),
                self.from_intent(intent="deny_eng", value=False)
            ],
            "quiz_level_1_question_3_eng": [
                self.from_intent(intent="affirm_eng", value=True),
                self.from_intent(intent="deny_eng", value=False)
            ],
            "quiz_level_1_question_4_eng": [
                self.from_intent(intent="affirm_eng", value=True),
                self.from_intent(intent="deny_eng", value=False)
            ],
            "quiz_level_1_question_5_eng": [
                self.from_intent(intent="affirm_eng", value=True),
                self.from_intent(intent="deny_eng", value=False)
            ]
        }

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:

        if not tracker.get_slot('quiz_eng'):
            return [FollowupAction('form_feedback_eng'), SlotSet('feedback_ctr_eng', 3)]

        if tracker.get_slot('quiz_level_1_question_5_eng') is not None:
            score = int(tracker.get_slot('quiz_level_1_question_5_eng')[0])
            values = [tracker.get_slot('quiz_level_1_question_1_eng'),tracker.get_slot('quiz_level_1_question_2_eng'),tracker.get_slot('quiz_level_1_question_3_eng'),
                      tracker.get_slot('quiz_level_1_question_4_eng'),tracker.get_slot('quiz_level_1_question_5_eng')]
            txt = ""
            for v in values:
                if v[3]=='wrong':
                    temp = f'For question {v[5]}; that was actually {v[2]} > {v[4]}'
                    txt = temp + "\n" + txt
            score_ = 5-score
            if score==5:
                dispatcher.utter_message(template="utter_score_full_eng")
            else:
                # dispatcher.utter_message(text=f"not bad your score is: correct answers: {score} wrong answers: {5-score}\n{txt}")
                dispatcher.utter_message(template="utter_score_eng", score=score, score_=score_)
                for v in values:
                    if v[3] == 'wrong':
                        dispatcher.utter_message(template="utter_score_feedback_eng", Q=v[5], A=v[2], feedback=v[4])

            return [FollowupAction('form_feedback_eng'), SlotSet('feedback_ctr_eng', 3),
                    SlotSet('quiz_eng', tracker.get_slot('quiz_eng')),
                    SlotSet('quiz_level_1_question_1_eng', None),
                    SlotSet('quiz_level_1_question_2_eng', None),
                    SlotSet('quiz_level_1_question_3_eng', None),
                    SlotSet('quiz_level_1_question_4_eng', None),
                    SlotSet('quiz_score_eng', tracker.get_slot('quiz_level_1_question_5_eng')[0]),
                    SlotSet('quiz_level_1_question_5_eng', None)]

    @staticmethod
    def quiz_level_1_question_1_eng_db() -> Dict[Text, Any]:
        with open('quiz_data.json') as f:
            data = json.load(f)
        dic = {}
        for i in range(0, len(data)):
            dic[str(data[i]['question']['ENG'])] = [data[i]['key'], str(data[i]['answer']['ENG'])]
        return dic

    def validate_quiz_level_1_question_1_eng(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        text = ''
        s = 0
        for event in tracker.events:
            if (event.get("event") == "bot") and (event.get("event") is not None):
                text = event.get("text")
        for i in self.quiz_level_1_question_1_eng_db().keys():
            if i == text:
                if value == self.quiz_level_1_question_1_eng_db()[i][0]:
                    s+=1
                    return {'quiz_level_1_question_1_eng': [s, text, str(self.quiz_level_1_question_1_eng_db()[i][0]), "correct", "feedback NA", 1]}
                else:
                    return {'quiz_level_1_question_1_eng': [s, text, str(self.quiz_level_1_question_1_eng_db()[i][0]), "wrong", str(self.quiz_level_1_question_1_eng_db()[i][1]), 1]}

    @staticmethod
    def quiz_level_1_question_2_eng_db() -> Dict[Text, Any]:
        with open('quiz_data.json') as f:
            data = json.load(f)
        dic = {}
        for i in range(0, len(data)):
            dic[str(data[i]['question']['ENG'])] = [data[i]['key'], str(data[i]['answer']['ENG'])]
        return dic

    def validate_quiz_level_1_question_2_eng(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        s = int(tracker.get_slot('quiz_level_1_question_1_eng')[0])
        text = ''
        for event in tracker.events:
            if (event.get("event") == "bot") and (event.get("event") is not None):
                text = event.get("text")
        for i in self.quiz_level_1_question_2_eng_db().keys():
            if i == text:
                if value == self.quiz_level_1_question_2_eng_db()[i][0]:
                    s+=1
                    return {'quiz_level_1_question_2_eng': [s, text, str(self.quiz_level_1_question_2_eng_db()[i][0]), "correct", "feedback NA", 2]}
                else:
                    return {'quiz_level_1_question_2_eng': [s, text, str(self.quiz_level_1_question_2_eng_db()[i][0]), "wrong", str(self.quiz_level_1_question_2_eng_db()[i][1]), 2]}


    @staticmethod
    def quiz_level_1_question_3_eng_db() -> Dict[Text, Any]:
        with open('quiz_data.json') as f:
            data = json.load(f)
        dic = {}
        for i in range(0, len(data)):
            dic[str(data[i]['question']['ENG'])] = [data[i]['key'], str(data[i]['answer']['ENG'])]
        return dic

    def validate_quiz_level_1_question_3_eng(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        s = int(tracker.get_slot('quiz_level_1_question_2_eng')[0])
        text = ''
        for event in tracker.events:
            if (event.get("event") == "bot") and (event.get("event") is not None):
                text = event.get("text")
        for i in self.quiz_level_1_question_3_eng_db().keys():
            if i == text:
                if value == self.quiz_level_1_question_3_eng_db()[i][0]:
                    s+=1
                    return {'quiz_level_1_question_3_eng': [s, text, str(self.quiz_level_1_question_3_eng_db()[i][0]), "correct", "feedback NA", 3]}
                else:
                    return {'quiz_level_1_question_3_eng': [s, text, str(self.quiz_level_1_question_3_eng_db()[i][0]), "wrong", str(self.quiz_level_1_question_3_eng_db()[i][1]), 3]}

    @staticmethod
    def quiz_level_1_question_4_eng_db() -> Dict[Text, Any]:
        with open('quiz_data.json') as f:
            data = json.load(f)
        dic = {}
        for i in range(0, len(data)):
            dic[str(data[i]['question']['ENG'])] = [data[i]['key'], str(data[i]['answer']['ENG'])]
        return dic

    def validate_quiz_level_1_question_4_eng(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        s = int(tracker.get_slot('quiz_level_1_question_3_eng')[0])
        text = ''
        for event in tracker.events:
            if (event.get("event") == "bot") and (event.get("event") is not None):
                text = event.get("text")
        for i in self.quiz_level_1_question_4_eng_db().keys():
            if i == text:
                if value == self.quiz_level_1_question_4_eng_db()[i][0]:
                    s+=1
                    return {'quiz_level_1_question_4_eng': [s, text, str(self.quiz_level_1_question_4_eng_db()[i][0]), "correct", "feedback NA", 4]}
                else:
                    return {'quiz_level_1_question_4_eng': [s, text, str(self.quiz_level_1_question_4_eng_db()[i][0]), "wrong", str(self.quiz_level_1_question_4_eng_db()[i][1]), 4]}

    @staticmethod
    def quiz_level_1_question_5_eng_db() -> Dict[Text, Any]:
        with open('quiz_data.json') as f:
            data = json.load(f)
        dic = {}
        for i in range(0, len(data)):
            dic[str(data[i]['question']['ENG'])] = [data[i]['key'], str(data[i]['answer']['ENG'])]
        return dic

    def validate_quiz_level_1_question_5_eng(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        s = int(tracker.get_slot('quiz_level_1_question_4_eng')[0])
        text = ''
        for event in tracker.events:
            if (event.get("event") == "bot") and (event.get("event") is not None):
                text = event.get("text")
        for i in self.quiz_level_1_question_5_eng_db().keys():
            if i == text:
                if value == self.quiz_level_1_question_5_eng_db()[i][0]:
                    s+=1
                    return {'quiz_level_1_question_5_eng': [s, text, str(self.quiz_level_1_question_5_eng_db()[i][0]), "correct", "feedback NA", 5]}
                else:
                    return {'quiz_level_1_question_5_eng': [s, text, str(self.quiz_level_1_question_5_eng_db()[i][0]), "wrong", str(self.quiz_level_1_question_5_eng_db()[i][1]), 5]}
    