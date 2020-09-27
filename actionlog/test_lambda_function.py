from lambda_function import process_payload, parse_event, lambda_handler, record_entry, update_summary
from unittest import mock
from moto import mock_dynamodb2
import boto3
import calendar
import time


ACTION_BIGARMS = '💪10'
MSG_EVENT_BODY = "%F0%9F%92%AA10"
MSG_FROM = '%2B16072152471'

def _table_setup():
    dynamodb = boto3.resource("dynamodb")
    tbl = dynamodb.create_table(
        TableName="actionlog-tables-statistics",
        KeySchema=[
            {"AttributeName": "member_id", "KeyType": "HASH"},
            {"AttributeName": "action", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "member_id", "AttributeType": "S"},
            {"AttributeName": "action", "AttributeType": "S"},
            {"AttributeName": "entry_count", "AttributeType": "N"},
            {"AttributeName": "time_updated", "AttributeType": "N"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        GlobalSecondaryIndexes=[
            {
                "IndexName": "member-updated-index",
                "KeySchema": [
                    {"AttributeName": "member_id", "KeyType": "HASH"},
                    {"AttributeName": "time_updated", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            }, {
                "IndexName": "action-updated-index",
                "KeySchema": [
                    {"AttributeName": "member_id", "KeyType": "HASH"},
                    {"AttributeName": "entry_count", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            }
        ]
    )
    tbl.put_item(Item={'member_id': '+16072152471', 'action': 'pushups', 'time_updated': 0, })
    tbl = dynamodb.create_table(
        TableName="actionlog-tables-entry",
        KeySchema=[
            {"AttributeName": "member_id", "KeyType": "HASH"},
            {"AttributeName": "time_created", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "member_id", "AttributeType": "S"},
            {"AttributeName": "time_created", "AttributeType": "N"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    # boto3.resource("dynamodb").get_available_subresources()
    # boto3.client('dynamodb').list_tables()
    tbl.put_item(Item={'member_id': '+16072152471', 'action': 'pushups', 'time_created': 0, 'value': 0})

def test_process_payload():
    result = process_payload(ACTION_BIGARMS)
    assert result == {
        'emoji_code': "flexed_biceps",
        'value': 10,
        'action': 'pushups',
    }

def test_parse_event():
    member_id, message = parse_event({
        'Body': MSG_EVENT_BODY,
        'From': MSG_FROM,
    })
    assert member_id == '+16072152471'
    assert message == ACTION_BIGARMS

@mock.patch('calendar.timegm')
@mock_dynamodb2
def test_record_entry(mock_time):
    _table_setup()
    mock_time.return_value = 1200000
    record_entry('+16072152471', {
        'action': 'pushups',
        'value': 10,
    })
    # get value updated

@mock_dynamodb2
def test_lambda_handler():
    _table_setup()
    message = lambda_handler({
        'Body': MSG_EVENT_BODY,
        'From': MSG_FROM,
    }, None)
    assert message == '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
           '<Response><Message><Body>10 pushups recorded over 1 entries</Body></Message></Response>'

@mock_dynamodb2
def test_update_summary():
    _table_setup()
    timestamp = calendar.timegm(time.gmtime())
    result, status = update_summary('+16072152471', 'pushups', 10, timestamp)
    assert status
    assert result['sum_total'] == 10