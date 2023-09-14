from unittest import mock

import emoji
from actionlog.lambda_function import (
    emoji_action,
    lambda_handler,
    parse_event,
    process_payload,
    record_entry,
)

MSG_EVENT_BODY = "%F0%9F%92%AA10"
MSG_FROM = "%2B16072152471"


def test_process_payload():
    result = process_payload("💪10")
    assert result == {
        "emoji_code": ":flexed_biceps:",
        "value": 10,
        "action": "pushups",
        "record": True,
        "message": ":flexed_biceps:10",
    }
    result = process_payload("💪🏻10")
    assert result == {
        "emoji_code": ":flexed_biceps_light_skin_tone:",
        "value": 10,
        "action": "pushups",
        "record": True,
        "message": ":flexed_biceps_light_skin_tone:10",
    }
    result = process_payload("10💪")
    assert result == {
        "value": 10,
        "action": "pushups",
        "person": None,
        "record": True,
        "message": "10:flexed_biceps:",
    }
    result = process_payload("10")
    assert result == {
        "value": 10,
        "action": "pushups",
        "person": None,
        "record": True,
        "message": "10",
    }
    result = process_payload("10 evan")
    assert result == {
        "value": 10,
        "action": "pushups",
        "person": "evan",
        "record": True,
        "message": "10 evan",
    }
    result = process_payload("Liked “💪27”")
    assert result == {"record": False, "message": "Liked “:flexed_biceps:27”"}


def test_parse_event():
    member_id, message = parse_event(
        {
            "Body": MSG_EVENT_BODY,
            "From": MSG_FROM,
        }
    )
    assert member_id == "+16072152471"
    assert message == "💪10"

    member_id, message = parse_event(
        {
            "Body": "10+evan",
            "From": MSG_FROM,
        }
    )
    assert member_id == "+16072152471"
    assert message == "10 evan"


@mock.patch("calendar.timegm")
def test_record_entry(mock_time, DDBT):
    mock_time.return_value = 1200000
    record_entry(
        "+16072152471",
        {
            "action": "pushups",
            "value": 10,
        },
    )
    # get value updated


@mock.patch("actionlog.lambda_function.message_members")
def test_lambda_handler(mock_message, DDBT):
    message = lambda_handler(
        {
            "Body": MSG_EVENT_BODY,
            "From": MSG_FROM,
        },
        None,
    )
    assert (
        message == '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<Response><Message><Body>10 pushups recorded over 1 meetings</Body></Message></Response>"
    )
    assert mock_message.call_count == 5
    calls = [
        mock.call("+16072152471", "💪10"),
        mock.call("+16073316619", "💪10"),
        mock.call("+18283356923", "💪10"),
        mock.call("+13214004992", "💪10"),
        mock.call("+16077675433", "💪10"),
    ]
    mock_message.assert_has_calls(calls)
    mock_message.reset_mock()

    message = lambda_handler(
        {
            "Body": "💪🏻10",
            "From": MSG_FROM,
        },
        None,
    )
    assert mock_message.call_count == 5
    mock_message.reset_mock()
    assert (
        message
        == """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Response><Message><Body>20 pushups recorded over 2 meetings</Body></Message></Response>"""
    )

    message = lambda_handler(
        {
            "Body": "10+evan",
            "From": MSG_FROM,
        },
        None,
    )
    assert (
        message
        == """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Response><Message><Body>Notified evan. 30 pushups recorded over 3 meetings</Body></Message></Response>"""
    )
    mock_message.assert_called_once_with("+16072152471", "10👍")
    mock_message.reset_mock()

    message = lambda_handler(
        {
            "Body": "10+roger",
            "From": MSG_FROM,
        },
        None,
    )
    mock_message.assert_not_called()
    mock_message.reset_mock()
    assert (
        message
        == """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Response><Message><Body>40 pushups recorded over 4 entries</Body></Message></Response>"""
    )

    message = lambda_handler(
        {
            "Body": "💪🏻10",
            "From": "+13214004992",
        },
        None,
    )
    mock_message.assert_called_once_with("+16072152471", "kelly: 💪🏻10")
    mock_message.reset_mock()
    assert (
        message
        == """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Response><Message><Body>10 pushups recorded over 1 meetings</Body></Message></Response>"""
    )

    message = lambda_handler(
        {
            "Body": "10 ❤️",
            "From": "+16073316619",
        },
        None,
    )
    mock_message.assert_called_once_with("+16072152471", "audrey: 10 ❤️")
    mock_message.reset_mock()
    assert (
        message
        == """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Response><Message><Body>10 pushups recorded over 1 entries</Body></Message></Response>"""
    )

    message = lambda_handler(
        {
            "Body": "10👍",
            "From": MSG_FROM,
        },
        None,
    )
    mock_message.assert_not_called()
    mock_message.reset_mock()
    assert (
        message
        == """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Response><Message><Body>50 pushups recorded over 5 entries</Body></Message></Response>"""
    )

    message = lambda_handler(
        {
            "Body": "☕️",
            "From": MSG_FROM,
        },
        None,
    )
    mock_message.assert_not_called()
    mock_message.reset_mock()
    assert (
        message
        == """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Response><Message><Body>1 caffeine recorded over 1 entries</Body></Message></Response>"""
    )


def test_emoji_action():
    assert "caffeine" == emoji_action(emoji.demojize("☕"))
    assert "pushups" == emoji_action(emoji.demojize("💪"))
    assert "pushups" == emoji_action(emoji.demojize("💪🏻"))
