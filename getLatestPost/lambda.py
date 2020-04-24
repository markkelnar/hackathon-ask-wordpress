"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6
For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""
from __future__ import print_function
from mls_stripper import MLStripper
import xmltodict
import requests
import email.utils
import re
from time import mktime
from datetime import datetime


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
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    # Dispatch to your skill's intent handlers
    if intent_name == "GetLatestPost":
        return get_latest_post(intent, session)
    elif intent_name == "ReadEntirePostIntent":
        return read_entire_post(intent, session)
    elif intent_name == "GetLatestPostsFromFavorites":
        return get_latest_post_from_favorites(intent, session)
    elif intent_name == "ReadLatestPostByIndex":
        return read_latest_post_by_index(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return handle_get_help_request(intent, session)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


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
    speech_output = "<speak><p>Fine Patrick.</p> I didn't feel like talking anyways.<break time=\"2s\"/><p>I am so lonely</p><p>I'm Misses Lonely.</p><p>I have nobody. To call my own.</p></speak>"

    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, markup_speechlet_response(
        card_title, speech_output, None, should_end_session))


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the blog reader " \
                    "What would you like me to do?"

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Can you ask Jason Short to quiet down so I can hear you?  I'm very sorry, lets try that again."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_get_help_request(intent, session):
    session_attributes = {}

    # Set a flag to track that we're in the Help state.
    speech_output = "I can read you information about blogs that you're interested in, so just ask me what you need. " \
                    "For example, say read me my favorite blog, or what's my latest blog post."
    reprompt_text = False
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))




def get_latest_post(intent, session):
    card_title = "Mark's Blog Post Content"
    session_attributes = {}

    r = requests.get('http://markkelnar.com/?feed=rss2', headers={'User-Agent': 'a user agent'})
    sitecontent = xmltodict.parse(r.content)

    items = sitecontent['rss']['channel']['item']
    title = items[0]['title'].encode("utf8")
    pub_date = items[0]['pubDate'].encode("utf8")
    days_ago = get_days_ago(pub_date)
    description = strip_tags(items[0]['description'])
    # description = re.sub(r'([^\s\w]|_)+', '', description)
    # description = say_wp(description)
    # comment_count = items[0]['slash:comments'].encode("utf8")
    # intro = ' '.join(description.split()[:25])

    speech_output = "Mark's latest post was - " + title + "."
    # speech_output = "Mark's latest post was - " + title + ". " + \
    #                 "It was published " + days_ago + " and it has " + comment_count + " comments. "\
    #                 "Here's a quick blurb. " + description + "."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I didn't get that, would you like me to read part of it?"
    should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_latest_post_from_favorites(intent, session):
    card_title = "Favorite Blog Posts Content"
    session_attributes = {}
    installs = [
        "wptavern.com",
        "torquemag.io"
    ]

    speech_output = "<speak>"
    for install in installs:
        url = "http://" + install + "/?feed=rss2"
        post_content = get_latest_post_content(url, install)
        speech_output += "The latest post for " + post_content['install'] + " was - " + post_content['title'] + ". " \
                         "It was published " + post_content['days_ago'] + " and it has " + post_content['comment_count'] + " comments. " \
                         "Here's a quick blurb. " + post_content['intro'] + "<break time=\"1s\"/>"
    speech_output += "</speak>"
    reprompt_text = "I didn't get that, would you like me to read part of it?"
    should_end_session = False

    return build_response(session_attributes, markup_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_latest_post_content(url, install):
    post_content = {}
    r = requests.get(url, headers={'User-Agent': 'a user agent'})
    sitecontent = xmltodict.parse(r.content)
    # TODO: Add items to session attributes
    item = sitecontent['rss']['channel']['item'][0]

    post_content['title'] = get_cleaned_title(item['title'].encode("utf8"))

    pub_date = item['pubDate'].encode("utf8")
    post_content['days_ago'] = get_days_ago(pub_date)
    post_content['description'] = get_cleaned_description(item['description'])
    post_content['intro'] = ' '.join(post_content['description'].split()[:25])
    post_content['comment_count'] = item['slash:comments'].encode("utf8")
    post_content['install'] = say_wp(install)
    return post_content


def get_cleaned_title(title):
    title = re.sub(r'([^\s\w]|_)+', '', title)
    return say_wp(title)


def get_cleaned_description(description):
    description = strip_tags(description)
    description = re.sub(r'([^\s\w]|_)+', '', description)
    return say_wp(description)


def say_wp(content):
    return content.replace("wp", "<say-as interpret-as=\"characters\">wp</say-as>")


def read_latest_post_by_index(intent, session):
    card_title = intent['name']
    session_attributes = {}
    site = {
        "1st": "torquemag.io",
        "2nd": "wpengine.com/blog",
        "3rd": "wptavern.com",
        "4th": "poststatus.com"
    }
    should_end_session = False
    if 'Index' in intent['slots']:
        index = intent['slots']['Index']['value']

        r = requests.get("http://" + site[index] + "/?feed=rss2", headers={'User-Agent': 'a user agent'})
        sitecontent = xmltodict.parse(r.content)
        items = sitecontent['rss']['channel']['item']
        install = say_wp(site[index])
        title = get_cleaned_title(items[0]['title'])
        content = get_cleaned_description(strip_tags(items[0]['description']))
        speech_output = "<speak>The latest post from " + install + ", titled " + title + \
                        ", reads <p>" + content + "</p></speak>"
        should_end_session = False
    else:
        speech_output = "I'm not sure which install you're interested in. " \
                        "You can say, first, second, third, fourth."
    reprompt_text = "I didn't get that. " \
                    "Why don't you come back once you've finished that food in your mouth?  Ew."
    return build_response(session_attributes, markup_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def create_latest_post_attributes(items):
    return {"latestPost": items}


def get_days_ago(pub_date):
    date_parsed = email.utils.parsedate(pub_date)
    dt = datetime.fromtimestamp(mktime(date_parsed))

    today = datetime.today()
    diff_date = today - dt  # timedelta object
    if diff_date.days > 1 and diff_date.seconds / 3600 > 1:
        return "%s days, %s hours ago" \
            % (diff_date.days, diff_date.seconds / 3600)
    elif diff_date.days is 1 and diff_date.seconds / 3600 > 1:
        return "%s day, %s hours ago" \
            % (diff_date.days, diff_date.seconds / 3600)
    elif diff_date.days > 1 and diff_date.seconds / 3600 is 1:
        return "%s days, %s hour ago" \
            % (diff_date.days, diff_date.seconds / 3600)
    elif diff_date.days is 1 and diff_date.seconds / 3600 is 1:
        return "%s day, %s hour ago" \
            % (diff_date.days, diff_date.seconds / 3600)
    elif diff_date.seconds / 3600 >= 1:
        return "%s hours ago" \
            % (diff_date.seconds / 3600)
    else:
        return "within the last hour"


def read_part_of_post(intent, session):
    card_title = intent['name']
    # speech_output = "Here's a quick blurb. Blurb Blurb Blog. Would you like to hear more?"

    if session.get('attributes', {}) and "latestPost" in session.get('attributes', {}):
        # session_attributes = session.get('attributes', {})
        latest_post = session['attributes']['latestPost']
        description = strip_tags(latest_post['description'])
        intro = ' '.join(description.split()[:20])
        speech_output = "Here's a quick blurb. " + intro
        should_end_session = False
    else:
        session_attributes = {}
        speech_output = "Just kidding. I wasn't able to get that blurb. Sorry."
        should_end_session = False

    reprompt_text = "I'm sorry, I didn't catch that. Do you want me to read part of this post for you? It looks pretty interesting."
    return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))


def read_entire_post(intent, session):
    card_title = intent['name']
    reprompt_text = "I'm sorry, I didn't catch that. Do you want me to read you your post? It looks pretty interesting."

    r = requests.get('http://torquemag.io/?feed=rss2', headers={'User-Agent': 'a user agent'})
    sitecontent = xmltodict.parse(r.content)

    items = sitecontent['rss']['channel']['item']
    session_attributes = create_latest_post_attributes(items[0])

    if "latestPost" in session.get('attributes', {}):
        latest_post = session['attributes']['latestPost']
        content = latest_post['content:encoded'].encode("utf8")
        speech_output = "Your latest blog post reads. " + latest_post['content']
        should_end_session = True
    else:
        speech_output = "Just kidding. I wasn't able to read your latest post."
        should_end_session = True

    return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'BlogReader - ' + title,
            'content': 'BlogReader - ' + output
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
            'title': "BlogReader - " + title,
            'content': "BlogReader - " + output
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
