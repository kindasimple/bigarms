from lambda_function import process_payload, parse_event, lambda_handler, record_entry
from unittest import mock

ACTION_BIGARMS = '💪10'
MSG_EVENT_BODY = "%F0%9F%92%AA10"
MSG_FROM = '%2B16072152471'

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
@mock.patch('lambda_function.dynamo')
def test_record_entry(mock_dynamo, mock_time):
    put_item = mock.Mock()
    mock_time.return_value = 1200000
    mock_dynamo.Table = mock.Mock(return_value=mock.Mock(put_item=put_item))
    record_entry('+16072152471', {
        'action': 'pushups',
        'value': 10,
    })
    put_item.assert_called_once_with(Item=
        {
            'member_id': '+16072152471',
            'time_created':  1200000,
            'action': 'pushups',
            'value': 10,
        }
    )

@mock.patch('lambda_function.record_entry')
def test_lambda_handler(_):
    message = lambda_handler({
        'Body': MSG_EVENT_BODY,
        'From': MSG_FROM,
    }, None)
    assert message == '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
           '<Response><Message><Body>Entry recorded!</Body></Message></Response>'