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
import boto3
import calendar
import emoji
import json
import re
import time
import time
import urllib.parse


print('Loading function')
ACTION_RE = re.compile('^:(?P<emoji_code>[a-zA-Z_]+):(?P<value>\d+)$')

ACTION_NUMBERS = {'pushups'}
EMOJI_ACTION_MAP = {
    'flexed_biceps': 'pushups'
}


def parse_event(event):
    message = urllib.parse.unquote(event['Body'])
    member_id = urllib.parse.unquote(event['From'])
    return member_id, message

def process_payload(message):
    """
    Process a text message body and return a dictionary with
    the action and the result value
    """
    message_text = emoji.demojize(message)
    result = ACTION_RE.match(message_text).groupdict()

    if EMOJI_ACTION_MAP[result['emoji_code']] in ACTION_NUMBERS:
        result['value'] = int(result['value'])
        result['action'] = EMOJI_ACTION_MAP[result['emoji_code']]
    return result

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

    status = None
    try:
        member_id, message = parse_event(event)
        input_dict = process_payload(message)
        summary, status = record_entry(member_id, input_dict)
    except Exception as e:
        print("Exception: " + repr(e))

    if status:
        return '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
           '<Response><Message><Body>{sum_total} {action} recorded over {entries} entries</Body></Message></Response>'.format(**summary)
    else:
       # TODO: Give some feedback
        return '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
           '<Response><Message><Body>What you talkin \'bout willis?</Body></Message></Response>'