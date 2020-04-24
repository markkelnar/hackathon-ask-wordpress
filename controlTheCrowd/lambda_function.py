"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "Crowd Control - " + title,
            'content': "To The Crowd - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def markup_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'card': {
            'type': 'Simple',
            'title': "Crowd Control - " + title,
            'content': "To The Crowd - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_help_response():
    return say("It sounds like you need some quiet time Patrick.")

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "After while crocodile"
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def say(text):
    session_attributes = {}
    card_title = "Team Member"
    speech_output = "<speak>" + text + "</speak>"
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, markup_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def say_hello():
    return say("Hello <say-as interpret-as=\"characters\">wp</say-as> engine..<break time=\"5s\"/>")

def say_brandon():
    return say("Hey Brandon......do something cool")

def say_dance_lights():
    return say("Echo ..... turn on dance lights.")

def say_spot_light():
    return say("Echo ..... turn on spot light.")

def say_warning():
    return say("Hello, please remain silent during the following program <break time=\"1s\"/>" \
        "I have sensitive ears and I can not hear my instructions clearly " \
        "if there is any background noise  <break time=\"1s\"/>" \
        "So please, hold all typing, laughing and clapping until the end of the show.  <break time=\"1s\"/>" \
        "With out further mumbo jumbo, hickory dickory dock ........ <break time=\"1s\"/>" \
        "Let the show begin"
    )

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent_name = ""
    if 'intent' in intent_request:
        intent = intent_request['intent']
        if 'name' in intent:
            intent_name = intent['name']

    # Dispatch to your skill's intent handlers
    if not intent_name:
        return get_help_response()
    elif intent_name == "Hello":
        return say_hello()
    elif intent_name == "Brandon":
        return say_brandon()
    elif intent_name == "Warning":
        return say_warning()
    elif intent_name == "Dance":
        return say_dance_lights()
    elif intent_name == "Spot":
        return say_spot_light()
    elif intent_name == "AMAZON.HelpIntent":
        return get_help_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
         return say_hello()
    return get_help_response()

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])