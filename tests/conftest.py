import pytest
import moto
import boto3
from unittest.mock import patch


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "as")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "at")


MOCK_TABLES = {
    "actionlog-tables-statistics": {
        'KeySchema': [
            {"AttributeName": "member_id", "KeyType": "HASH"},
            {"AttributeName": "action", "KeyType": "RANGE"},
        ],
        'AttributeDefinitions': [
            {"AttributeName": "member_id", "AttributeType": "S"},
            {"AttributeName": "action", "AttributeType": "S"},
            {"AttributeName": "entry_count", "AttributeType": "N"},
            {"AttributeName": "time_updated", "AttributeType": "N"},
        ],
        'ProvisionedThroughput': {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        'GlobalSecondaryIndexes': [
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
            },
            {
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
    },
    "actionlog-tables-entry": {
        "KeySchema": [
            {"AttributeName": "member_id", "KeyType": "HASH"},
            {"AttributeName": "time_created", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "member_id", "AttributeType": "S"},
            {"AttributeName": "time_created", "AttributeType": "N"},
        ],
        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    }
}

MOCK_ENTRIES = {
    "actionlog-tables-statistics": [
        {
            "member_id": "+16072152471",
            "action": "pushups",
            "time_updated": 0,
        },
    ],
    "actionlog-tables-entry": [{
        "member_id": "+16072152471",
        "action": "pushups",
        "time_created": 0,
        "value": 0,
    }]
}


@pytest.fixture
def DDBT():
    with moto.mock_dynamodb2():
        client = boto3.client("dynamodb", region_name="us-west-2")
        for table_name, table_config in MOCK_TABLES.items():
            client.create_table(
                TableName=table_name,
                **table_config
            )
        db = boto3.resource("dynamodb", region_name="us-west-2")
        for table_name, table_items in MOCK_ENTRIES.items():
            tbl = db.Table(table_name)
            for item in table_items:
                tbl.put_item(Item=item)

        # boto3.resource("dynamodb").get_available_subresources()
        # boto3.client('dynamodb').list_tables()
        with patch('src.actionlog.actionlog.db_resource', return_value=db):
            yield db
