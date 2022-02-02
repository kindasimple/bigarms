import calendar
import json
import time
import botocore
from collections import defaultdict
import boto3
import os
from typing import List

from pydantic import BaseModel

from .constants import ACTION_PUSHUP_ID_NAME

TABLE_STATISTICS = "actionlog-tables-statistics"
REGION = 'us-west-2'
# REGION = 'local'


class LeaderboardEntry(BaseModel):
    member_id: str
    member_name: str
    action: str
    entries: int = 0
    sum_total: int = 0
    time_updated: int


def db_kwargs():
    return {
        'endpoint_url': os.getenv('ENDPOINT_URL'),
        'aws_access_key_id': '',
        'aws_secret_access_key': '',
    } if os.getenv('ENDPOINT_URL') else {}


def db_client():
    session = boto3.session.Session()
    kwargs = db_kwargs()
    client = session.client(
        service_name='dynamodb',
        region_name=REGION,
        **kwargs
    )
    return client


def db_resource():
    kwargs = db_kwargs()
    db = boto3.resource(
        service_name='dynamodb',
        region_name=REGION,
        **kwargs)
    return db


def update_summary(member_id, action, value, timestamp):
    db = db_resource()
    table = db.Table(TABLE_STATISTICS)

    result = table.update_item(
        Key={"member_id": member_id, "action": action},
        UpdateExpression="ADD entries :one, sum_total :value SET time_updated = :tu",
        ExpressionAttributeValues={
            ":one": 1,
            ":value": value,
            ":tu": timestamp,
        },
        ReturnValues="ALL_NEW",
    )
    return result["Attributes"], result["ResponseMetadata"]["HTTPStatusCode"] == 200


def get_summary(action: str) -> List[LeaderboardEntry]:
    db = db_resource()
    table = db.Table(TABLE_STATISTICS)

    done, start_key = False, False
    items = []
    scan_kwargs = {}
    while not done:
        if start_key:
            scan_kwargs['ExclusiveStartKey'] = start_key
        try:
            response = table.scan(**scan_kwargs)
        except botocore.exceptions.ClientError as e:
            print(e.response['Error']['Message'])
            raise
        else:
            items = response.get('Items', []) + items
            start_key = response.get('LastEvaluatedKey', None)
            done = start_key is None

    leaderboard = defaultdict(dict)
    for item in items:
        if item['action'] != action:
            continue
        member_id = item['member_id']
        leaderboard[member_id] = item
        leaderboard[member_id]['member_name'] = ACTION_PUSHUP_ID_NAME.get(member_id, member_id)

    return [
        LeaderboardEntry(**item)
        for member_id, item in leaderboard.items()]


def record_entry(member_id, input_data):
    # TODO: retrieve the current summary data and include it
    timestamp = calendar.timegm(time.gmtime())
    item_dict = {
        "member_id": member_id,
        "time_created": timestamp,
        "action": input_data["action"],
        "value": input_data["value"],
    }
    print("saving item %s" % json.dumps(item_dict))
    db = db_resource()
    table = db.Table("actionlog-tables-entry")
    table.put_item(Item=item_dict)
    return update_summary(
        member_id, input_data["action"], input_data["value"], timestamp
    )
