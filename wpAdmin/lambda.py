"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6
For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""
from __future__ import print_function
import email.utils
from time import mktime
from datetime import datetime

from wpadmin import WpAdmin

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
        on_session_started({'requestId': event['request']['requestId']}, event['session'])
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def create_attributes(session, title, post_id):
    #if title:
    #    session['attributes']["title"] = title
    #if post_id:
    #    session['attributes']["post_id"] = post_id
    return session['attributes']

def session_save_title(session, title):
    if not session.get('attributes', {}):
        session['attributes'] = {}
    session['attributes']['title'] = title
    return session['attributes']

def session_save_post_id(session, post_id):
    if not session.get('attributes', {}):
        session['attributes'] = {}
    session['attributes']['post_id'] = post_id
    return session['attributes']

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


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
    if intent_name == "GetPosts":
        return get_posts()
    elif intent_name == "StartPost":
        return play_message(message="You'll need to give it a title.", title="Ask Title")
    elif intent_name == "SetTitle":
        return capture_title(intent, session)
    elif intent_name == "RecordPost":
        return capture_post_content(intent, session)
    elif intent_name == "PlayPost":
        return play_that_post(intent, session)
    elif intent_name == "PublishPost":
        return publish_that_post(intent, session)
    elif intent_name == "DoWhatNow":
        return get_command()
    elif intent_name == "GetComments":
        return get_comments()
    elif intent_name == "Dance":
        return play_message(message="Echo ..... turn on dance lights.")
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        return get_welcome_response()


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here
# --------------- Functions that control the skill's behavior ------------------


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thanks! Have a nice day!"

    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def play_message(message, title="Play message"):
    session_attributes = {}
    card_title = title
    speech_output = message
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_todo():
    return play_message("This command is not implemted yet", title="To do")

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Let's log into your site"

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "There's too much background noise. Please try again"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def capture_title(intent, session):
    session_attributes = {}
    card_title = "Get Title"

    if 'Title' in intent['slots'] and 'value' in intent['slots']['Title']:
        heard_title = intent['slots']['Title']['value']
        session_attributes = session_save_title(session, title=heard_title)
        speech_output = "Here's what I heard for the title: " + heard_title
    else:
        speech_output = "I didn't hear that. Please try again."

    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
    
def capture_post_content(intent, session):
    session_attributes = {}
    card_title = "Get Post Content"

    if session.get('attributes', {}) and "title" in session.get('attributes', {}):
        # session_attributes = session.get('attributes', {})
        title = session['attributes']['title']
    else:
        title = "couldn't find it in the session data"

    if 'Post' in intent['slots'] and 'value' in intent['slots']['Post']:
        heard_content = intent['slots']['Post']['value']
        wp = WpAdmin()
        post_id = wp.createPost(title=title, content=heard_content)
        session_attributes = session_save_post_id(session, post_id=post_id)
        speech_output = "Here's what I heard " + heard_content
    else:
        speech_output = "I didn't hear that. Please try again."

    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def play_that_post(intent, session):
    session_attributes = {}
    card_title = "Read Post Content"

    if session.get('attributes', {}) and "post_id" in session.get('attributes', {}):
        post_id = session['attributes']['post_id']
        session_attributes = session['attributes']
        wp = WpAdmin()
        speech_output = wp.getPostContent(post_id=post_id)
    else:
        speech_output = "I had a problem loading that post."

    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def publish_that_post(intent, session):
    session_attributes = {}
    card_title = "Publish Post Content"

    if session.get('attributes', {}) and "post_id" in session.get('attributes', {}):
        post_id = session['attributes']['post_id']
        session_attributes = session['attributes']
        wp = WpAdmin()
        wp.publishPost(post_id)
        speech_output = "Your post has been published. How did I do?"
    else:
        speech_output = "I had a problem loading that post."

    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_posts():
    session_attributes = {}
    card_title = "Get Posts"

    wp = WpAdmin()
    posts = wp.getPosts()
    speech_output = "From your last 10 posts. " \
        "You have "+str(len(posts['drafts']))+" published posts. " \
        "And "+str(len(posts['published']))+" drafts in progress. "

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "There's too much background noise. Please try again"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_command():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Say something you want for me to do. " \
        "You can say something like, create blog post or count comments."

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "There's too much background noise. Please try again"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_comments():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Getting comments for you"

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "There's too much background noise. Please try again"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))



# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
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
