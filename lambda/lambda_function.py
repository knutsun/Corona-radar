# -*- coding: utf-8 -*-

import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Context

from ask_sdk_model import Response

import csv
import pandas as pd
import requests


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

states = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DC": "Washington D.C.",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "PR": "Puerto Rico",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}

state_geoids = {
    "AL": "01",
    "AK": "02",
    "AZ": "04",
    "CA": "06",
    "CO": "08",
    "CT": "09",
    "DE": "10",
    "DC": "11",
    "FL": "12",
    "GA": "13",
    "HI": "15",
    "ID": "16",
    "IL": "17",
    "IN": "18",
    "IA": "19",
    "KS": "20",
    "KY": "21",
    "LA": "22",
    "ME": "23",
    "MD": "24",
    "MA": "25",
    "MI": "26",
    "MN": "27",
    "MS": "28",
    "MO": "29",
    "MT": "30",
    "NE": "31",
    "NV": "32",
    "NH": "33",
    "NJ": "34",
    "NM": "35",
    "NY": "36",
    "NC": "37",
    "ND": "38",
    "OH": "39",
    "OK": "40",
    "OR": "41",
    "PA": "42",
    "RI": "44",
    "SC": "45",
    "SD": "46",
    "TN": "47",
    "TX": "48",
    "VT": "50",
    "VA": "51",
    "WA": "53",
    "WV": "54",
    "WI": "55",
    "WY": "56",
    "AS": "60",
    "GU": "66",
    "MP": "69",
    "PW": "70",
    "PR": "72",
    "VI": "78"
}

urls = {
    "states": "http://coronavirusapi.com/states.csv",
    "time_series": "http://coronavirusapi.com/time_series.csv",
    "time_series_by_state": "http://coronavirusapi.com/getTimeSeries/"
}

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello! Welcome to Corona radar! \
            You can ask questions like 'How many people have died in Texas'"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Go ahead, ask a question.")
                .response
        )

class GetLocationIntentHandler(AbstractRequestHandler):
    """Handler for GetLocation Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetLocationIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        accessToken = handler_input.request_envelope.context.system.api_access_token
        device_id = handler_input.request_envelope.context.system.device.device_id
        url = 'https://api.amazonalexa.com/v1/devices/{}/settings/address'.format(device_id)
        headers = {
            'Authorization': 'Bearer ' + accessToken, 
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers)
        
        address_line_one = response.json()['addressLine1']
        city = response.json()['city']
        state_or_region = response.json()['stateOrRegion']
        

        address_url = 'http://www.yaddress.net/api/address'
        data = {
            "AddressLine1": address_line_one,
            "AddressLine2": '{} {}'.format(city, state_or_region)
        }
        county_response = requests.get(address_url, data=data)
        
        nyt_url = 'https://static01.nyt.com/newsgraphics/2020/03/16/coronavirus-maps/c17bfa1a1aeb007490a5a6ca6ee7996ccefbe617/data/timeseries/en/USA-{}.json'.format(state_geoids[state_or_region])
        nyt_response = requests.get(nyt_url)
        nyt = ''
        for data in nyt_response.json()['data']:
            if data['display_name'].upper() == str(county_response.json()['County']).upper():
                nyt = data['latest']['deaths']
        speak_output = '{} people have died from coronavirus in {} county'.format(nyt, str(county_response.json()['County']))

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response)

class GetCovidNumbersIntentHandler(AbstractRequestHandler):
    """Handler for GetCovidNumbers Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetCovidNumbersIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        slots = handler_input.request_envelope.request.intent.slots
        state_slot = slots["state"].value

        df = pd.read_csv(urls['states'])
        
        speak_output = ''

        for index, state in df.iterrows():
            for index, st in enumerate(states):
                if state[0] == st:
                    if states[st] == state_slot:
                        speak_output = speak_output + state_slot + ' has had ' + str(state[3]) + ' deaths from coronavirus'

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class GetTopCovidNumbersIntentHandler(AbstractRequestHandler):
    """Handler for GetTopCovidNumbers Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetTopCovidNumbersIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        slots = handler_input.request_envelope.request.intent.slots

        number_slot = slots["number"].value

        df = pd.read_csv(urls["states"])
        
        speak_output = ''

        data_struc = {
        }

        for index, state in df.iterrows():
            for index, st in enumerate(states):
                if state[0] == st:
                    data_struc[state[0]] = state[3]

        ordered_struc = sorted(data_struc.items(), key=lambda x: x[1], reverse=True)

        for state, count in enumerate(ordered_struc[:int(number_slot)]):
            speak_output = speak_output + ' ' + str(states[count[0]]) + ' with ' + str(count[1]) + ' deaths. '

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class GetBottomCovidNumbersIntentHandler(AbstractRequestHandler):
    """Handler for GetBottomCovidNumbers Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetBottomCovidNumbersIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        slots = handler_input.request_envelope.request.intent.slots

        number_slot = slots["number"].value

        df = pd.read_csv(urls["states"])
        
        speak_output = ''

        data_struc = {
        }

        for index, state in df.iterrows():
            for index, st in enumerate(states):
                if state[0] == st:
                    data_struc[state[0]] = state[3]

        ordered_struc = sorted(data_struc.items(), key=lambda x: x[1], reverse=False)

        for state, count in enumerate(ordered_struc[:int(number_slot)]):
            speak_output = speak_output + ' ' + str(states[count[0]]) + ' with ' + str(count[1]) + ' deaths. '

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetLocationIntentHandler())
sb.add_request_handler(GetCovidNumbersIntentHandler())
sb.add_request_handler(GetTopCovidNumbersIntentHandler())
sb.add_request_handler(GetBottomCovidNumbersIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()