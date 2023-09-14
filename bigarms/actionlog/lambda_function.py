"""
Receive messages sent via text to twilio and store them in dynamodb
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
import inspect
import json
import os
import re
from typing import Any, Dict, Tuple
from urllib import parse, request

import emoji

from .actionlog import record_entry
from .constants import ACTION_PUSHUP_ID_NAME

print("Loading function")
ACTION_CALL_PUSHUPS_RE = re.compile(r"^(?P<emoji_code>:[a-zA-Z_]+:)(?P<value>\d+)$")
ACTION_CALL_RE = re.compile(r"^(?P<emoji_code>:[a-zA-Z_]+:)(?P<value>\d+)?$")
# ACTION_RESPOND_RE = re.compile('^(?P<value>\\d+)(:[a-zA-Z_]+:)?$')
ACTION_RESPOND_RE = re.compile(
    "^(?P<value>\\d+)\\s*?(:[a-zA-Z_]+:)?\\s*?(?P<person>\\w+)?$"
)
ACTION_NUMBERS = {"pushups"}
EMOJI_ACTION_MAP = {
    ":flexed_biceps:": "pushups",
    ":hot_beverage:": "caffeine",
}
ACTION_SET = {action for code, action in EMOJI_ACTION_MAP.items()}
ACTION_CLUB_MAP = {"pushups": ACTION_PUSHUP_ID_NAME}
OWNED_NUMBER = "+12526295051"
CLUB_MANAGER = "+16072152471"
TWILIO_SMS_URL = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json"


def _xml(message) -> str:
    return inspect.cleandoc(
        f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response><Message><Body>{message}</Body></Message></Response>
    """
    )


def twilio_req():
    populated_url = TWILIO_SMS_URL.format(os.environ["TWILIO_ACCOUNT_SID"])
    req = request.Request(populated_url)
    authentication = "{}:{}".format(
        os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"]
    )
    base64string = base64.b64encode(authentication.encode("utf-8"))
    req.add_header("Authorization", "Basic %s" % base64string.decode("ascii"))
    return req


def message_members(to_number, body):
    # from twilio.rest import Client
    # client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
    # message = client.messages.create(
    #     to=num,
    #     from_=from_number,
    #     body=f'💪{value}',
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
            print("Twilio returned {}".format(str(f.read().decode("utf-8"))))
    except Exception as e:
        # something went wrong!
        raise e


def parse_event(event: Dict[str, str]) -> Tuple[str, str]:
    message = parse.unquote_plus(event["Body"]).strip()
    member_id = parse.unquote(event["From"])
    return member_id, message


def emoji_action(emoji_code: str) -> str:
    if not emoji_code:
        return
    if emoji_code in EMOJI_ACTION_MAP:
        return EMOJI_ACTION_MAP[emoji_code]
    for emoji_, action in EMOJI_ACTION_MAP.items():
        if emoji_code.startswith(emoji_[:-1] + "_"):
            return action


def process_payload(message) -> Dict[str, Any]:
    """
    Process a text message body and return a dictionary with
    the action and the result value
    """
    message_text = emoji.demojize(message)

    # Process new meetings from any organizer
    match = ACTION_CALL_PUSHUPS_RE.match(message_text)
    if match:
        result = match.groupdict()
        if emoji_action(result["emoji_code"]) in ACTION_NUMBERS:
            result["value"] = int(result["value"])
            result["action"] = emoji_action(result["emoji_code"])
            result["message"] = message_text
            result["record"] = True
            return result

    # Process new actions
    match = ACTION_CALL_RE.match(message_text)
    if match:
        result = match.groupdict()
        if emoji_action(result["emoji_code"]) in ACTION_SET:
            result["value"] = int(result.get("value") or 1)
            result["action"] = emoji_action(result["emoji_code"])
            result["message"] = message_text
            result["record"] = True
            return result

    # process meeting responses from participants
    match = ACTION_RESPOND_RE.match(message_text)
    if match:
        result = match.groupdict()
        if result["value"]:
            result["value"] = int(result["value"])
            result["action"] = "pushups"
            result["message"] = message_text
            result["record"] = True
        return result

    # process random messages
    return {"record": False, "message": message_text}


def lambda_handler(event: Dict, context: Any) -> str:
    """
    parse a message of the format <emoji><value> and store it in
    a dynamodb table
    """
    print("Received event: " + json.dumps(event, indent=2))
    # to_number = event['To']
    # from_number = event['From']
    status = None
    try:
        member_id, message = parse_event(event)
        input_dict = process_payload(message)
        if input_dict["record"]:
            summary, status = record_entry(member_id, input_dict)
        else:
            status = True

    except Exception as e:
        print("Exception: ", repr(e))
        raise e

    if status:
        action = emoji_action(input_dict.get("emoji_code"))
        if action == "pushups":
            if member_id == CLUB_MANAGER:
                for to_number in ACTION_CLUB_MAP["pushups"]:
                    message_members(to_number, f'💪{input_dict["value"]}')
                return _xml(
                    "{sum_total} {action} recorded over {entries} meetings".format(
                        **summary
                    )
                )
            else:
                name = ACTION_CLUB_MAP["pushups"][member_id]
                message_members(CLUB_MANAGER, f"{name}: {message}")
                return _xml(
                    "{sum_total} {action} recorded over {entries} meetings".format(
                        **summary
                    )
                )

        elif input_dict["record"]:
            name_member_id_map = {
                name: member_id for member_id, name in ACTION_PUSHUP_ID_NAME.items()
            }
            person = (input_dict.get("person") or "").lower()
            if member_id == CLUB_MANAGER:
                if person in name_member_id_map:
                    # Send a labeled confirmation to the target member
                    to_number = name_member_id_map[person]
                    message_members(to_number, f"{input_dict['value']}👍")
                    return _xml(
                        "Notified {person}. {sum_total} {action} recorded over {entries} meetings".format(
                            person=person, **summary
                        )
                    )
            else:
                # Send a member's reply to the manager
                person = ACTION_PUSHUP_ID_NAME[member_id]
                message_members(CLUB_MANAGER, f"{person}: {message}")
            return _xml(
                "{sum_total} {action} recorded over {entries} entries".format(**summary)
            )
        else:
            # someone is trying to chat or like
            person = ACTION_PUSHUP_ID_NAME[member_id]
            message_members(CLUB_MANAGER, f"{person}: {message}")
            return None
    else:
        # TODO: Give some feedback
        return _xml("oh dear!")
