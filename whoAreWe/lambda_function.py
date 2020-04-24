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
            'title': "The Team - " + title,
            'content': "Who Are We? - " + output
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
            'title': "The Team - " + title,
            'content': "Who Are We? - " + output
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
    session_attributes = {}
    card_title = "Help"
    speech_output = "<speak>Let's get ready to rumble! Dramatic pause <break time=\"3s\"/> " \
        "Now let's go." \
        "</speak>" 
    #    "<audio src=\"https://carfu.com/audio/carfu-welcome.mp3\" />"
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, markup_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Go get them team.  " \
        "Let's show them what I can do. " \
        "I'll try not to screw it up."

    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def say(name):
    session_attributes = {}
    card_title = "Team Member"
    speech_output = "<speak>" + name + "<break time=\"2s\"/></speak>"
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, markup_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def say_patrick():
    return say("We have Paatrick")

def say_mark():
    return say("Then we have Maark")

def say_john():
    return say("We have John. but we call him the intern.")

def say_george():
    return say("And everyone loves gorgeous George Mathew")

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
    elif intent_name == "WhoAreWe":
        return say_patrick()
    elif intent_name == "WhoNext":
        return say_mark()
    elif intent_name == "WhoElse":
        return say_john()
    elif intent_name == "AndLast":
        return say_george()
    elif intent_name == "AMAZON.HelpIntent":
        return get_help_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
         return say_patrick(intent, session)
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