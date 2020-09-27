import pytest
import moto
import boto3

@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv('TWILIO_ACCOUNT_SID', 'as')
    monkeypatch.setenv('TWILIO_AUTH_TOKEN', 'at')

@pytest.fixture
def DDBT():
     with moto.mock_dynamodb2():
        client = boto3.client('dynamodb')
        client.create_table(
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
        tbl = boto3.resource('dynamodb').Table("actionlog-tables-statistics")
        tbl.put_item(Item={'member_id': '+16072152471', 'action': 'pushups', 'time_updated': 0, })
        client.create_table(
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
        tbl = boto3.resource('dynamodb').Table("actionlog-tables-entry")
        tbl.put_item(Item={'member_id': '+16072152471', 'action': 'pushups', 'time_created': 0, 'value': 0})
        yield tbl