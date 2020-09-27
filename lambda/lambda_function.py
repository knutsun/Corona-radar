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
        
        # slots = handler_input.request_envelope.request.intent.slots
        # state_slot = slots["state"].value
        accessToken = handler_input.request_envelope.context.system.api_access_token
        device_id = handler_input.request_envelope.context.system.device.device_id
        response = requests.get('https://api.amazonalexa.com/v1/devices/{}/settings/address'.format(str(device_id)),
        headers={'Authorization: Bearer '.format(str(accessToken)),
                'Accept: application/json'  })
        
        
        speak_output = '{}'.format(str(response.json()))

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