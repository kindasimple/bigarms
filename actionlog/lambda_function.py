"""
Recieve messages sent via text to twilio and store them in dynamodb
with a schema format
    -
    AttributeName: "member_id"
    AttributeType: "S"
    -
    AttributeName: "entry_count"
    AttributeType: "N"
    -
    AttributeName: "time_created"
    AttributeType: "N"
"""
import base64
import calendar
import json
import os
import re
import time
from urllib import parse, request

import boto3
import emoji

print('Loading function')
ACTION_CALL_RE = re.compile('^:(?P<emoji_code>[a-zA-Z_]+):(?P<value>\d+)$')
# ACTION_RESPOND_RE = re.compile('^(?P<value>\\d+)(:[a-zA-Z_]+:)?$')
ACTION_RESPOND_RE = re.compile('^(?P<value>\\d+)\\s*?(:[a-zA-Z_]+:)?\\s*?(?P<person>\\w+)?$')

ACTION_NUMBERS = {'pushups'}
EMOJI_ACTION_MAP = {
    'flexed_biceps': 'pushups',
}
# ACTION_PUSHUP_ID_NAME = {'+16072152471': 'evan'}
ACTION_PUSHUP_ID_NAME = {
    '+16072152471': 'evan',
    '+16073316619': 'audrey',
    '+18283356923': 'gabby',
    '+13214004992': 'kelly',
    '+16077675433': 'atalyia',
}
ACTION_CLUB_MAP = {'pushups': ACTION_PUSHUP_ID_NAME}
OWNED_NUMBER = '+12526295051'
CLUB_MANAGER = '+16072152471'

TWILIO_SMS_URL = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json"

def twilio_req():
    populated_url = TWILIO_SMS_URL.format(os.environ['TWILIO_ACCOUNT_SID'])
    req = request.Request(populated_url)
    authentication = "{}:{}".format(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
    base64string = base64.b64encode(authentication.encode('utf-8'))
    req.add_header("Authorization", "Basic %s" % base64string.decode('ascii'))
    return req

def message_members(to_number, body):
    # from twilio.rest import Client
    # client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
    # message = client.messages.create(
    #     to=num,
    #     from_=from_number,
    #     body='💪{}'.format(value)
    # )
    # print(message.sid)
    post_params = {
        "To": to_number,
        "From": OWNED_NUMBER,
        "Body": emoji.emojize(body),
    }
    data = parse.urlencode(post_params).encode()
    req = twilio_req()
    try:
        # perform HTTP POST request
        with request.urlopen(req, data) as f:
            print("Twilio returned {}".format(str(f.read().decode('utf-8'))))
    except Exception as e:
        # something went wrong!
        raise e


def parse_event(event):
    message = parse.unquote_plus(event['Body']).strip()
    member_id = parse.unquote(event['From'])
    return member_id, message

def emoji_action(emoji_code):
    if not emoji_code:
        return
    if emoji_code in EMOJI_ACTION_MAP:
        return EMOJI_ACTION_MAP[emoji_code]
    for emoji, action in EMOJI_ACTION_MAP.items():
        if emoji_code.startswith(emoji + '_'):
            return action

def process_payload(message):
    """
    Process a text message body and return a dictionary with
    the action and the result value
    """
    message_text = emoji.demojize(message)

    # Process new meetings from any organizer
    match = ACTION_CALL_RE.match(message_text)

    if match:
        result = match.groupdict()
        if emoji_action(result['emoji_code']) in ACTION_NUMBERS:
            result['value'] = int(result['value'])
            result['action'] = emoji_action(result['emoji_code'])
            result['message'] = message_text
            result['record'] = True
            return result

    # process meeting responses from participants
    match = ACTION_RESPOND_RE.match(message_text)
    if match:
        result = match.groupdict()
        if result['value']:
            result['value'] = int(result['value'])
            result['action'] = 'pushups'
            result['message'] = message_text
            result['record'] = True
        return result

    # process random messages
    return {'record': False, 'message': message_text}

def record_entry(member_id, input_data):
    """
    """
    # TODO: retrieve the current summary data and include it
    timestamp = calendar.timegm(time.gmtime())
    item_dict = {
        'member_id': member_id,
        'time_created': timestamp,
        'action': input_data['action'],
        'value': input_data['value'],
    }
    print('saving item %s' % json.dumps(item_dict))
    dynamo = boto3.resource('dynamodb')
    table = dynamo.Table('actionlog-tables-entry')
    table.put_item(
        Item=item_dict
    )
    return update_summary(member_id, input_data['action'], input_data['value'], timestamp)


def update_summary(member_id, action, value, timestamp):
    dynamo = boto3.resource('dynamodb')
    table = dynamo.Table('actionlog-tables-statistics')
    result = table.update_item(
        Key={'member_id': member_id, 'action': action},
        UpdateExpression="ADD entries :one, sum_total :value SET time_updated = :tu",
        ExpressionAttributeValues={
            ':one': 1,
            ':value': value,
            ':tu': timestamp,
        },
        ReturnValues='ALL_NEW',
    )
    return result['Attributes'], result['ResponseMetadata']['HTTPStatusCode'] == 200

def lambda_handler(event, context):
    """
    parse a message of the format <emoji><value> and store it in a dynamodb table
    """
    print("Received event: " + json.dumps(event, indent=2))
    # to_number = event['To']
    # from_number = event['From']
    status = None
    try:
        member_id, message = parse_event(event)
        input_dict = process_payload(message)
        if input_dict['record']:
            summary, status = record_entry(member_id, input_dict)
        else:
            status = True

    except Exception as e:
        print("Exception: ", repr(e))
        raise e


    if status:
        emoji_code = input_dict.get('emoji_code')
        if emoji_action(emoji_code) == 'pushups':
            print('TODO: Send call to action to', ACTION_CLUB_MAP.get(summary['action']))
            if member_id == CLUB_MANAGER:
                for to_number in ACTION_CLUB_MAP['pushups']:
                    message_members(to_number, '💪{}'.format(input_dict['value']))
                return '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
                '<Response><Message><Body>{sum_total} {action} recorded over {entries} meetings</Body></Message></Response>'.format(**summary)
            else:
                name = ACTION_CLUB_MAP['pushups'][member_id]
                return '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
                '<Response><Message><Body>{name} does {value} {action}</Body></Message></Response>'.format(name=name, **summary)
        elif input_dict['record']:
            name_member_id_map = {name: member_id for member_id, name in ACTION_PUSHUP_ID_NAME.items()}
            person = (input_dict.get('person') or '').lower()
            if member_id == CLUB_MANAGER:
                if person in name_member_id_map:
                    # Send a labeled confirmation to the target member
                    to_number = name_member_id_map[person]
                    message_members(to_number, '{}👍'.format(input_dict['value']))

                    return '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
                    '<Response><Message><Body>Notified {person}. {sum_total} {action} recorded over {entries} meetings</Body></Message></Response>'.format(person=person, **summary)
            else:
                # Send a member's reply to the manager
                person = ACTION_PUSHUP_ID_NAME[member_id]
                message_members(CLUB_MANAGER, '{}: {}'.format(person, message))
            return '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
            '<Response><Message><Body>{sum_total} {action} recorded over {entries} entries</Body></Message></Response>'.format(**summary)
        else:
            # someone is trying to chat or like
            person = ACTION_PUSHUP_ID_NAME[member_id]
            message_members(CLUB_MANAGER, '{}: {}'.format(person, message))
            return None
    else:
       # TODO: Give some feedback
        return '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
           '<Response><Message><Body>What you talkin \'bout willis?</Body></Message></Response>'
