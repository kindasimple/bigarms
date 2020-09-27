from __future__ import print_function
import time
import boto3
import json

print('Loading function')
dynamo = boto3.client('dynamodb')


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def lambda_handler(event, context):
    print("Received event: " + str(event))
    epoch = time.time()
    time_created = time.gmtime(epoch)

    return '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
           '<Response><Message><Body>Hello world! -Lambda</Body><Media>https://demo.twilio.com/owl.png</Media></Message></Response>'

def process_payload(message_dict):
    pass

def create_result(result_data):
    pass

def attend_result(result_data):
    pass

def update_result(result_data):
    pass

def lambda_handler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.

    To scan a DynamoDB table, make a GET request with the TableName as a
    query string parameter. To put, update, or delete an item, make a POST,
    PUT, or DELETE request respectively, passing in the payload to the
    DynamoDB API as a JSON body.
    '''
    #print("Received event: " + json.dumps(event, indent=2))

    message = json.loads(event['body'])
    operation, input_data = process_payload(message)

    if operation == 'create_meeting':
        # create a new record
        result_data = create_result(input_data)
        dynamo.put_item(**result_data)
        # TODO: Update club members
        return  '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
           '<Response><Message><Body>Meeting Started!</Body></Message></Response>'
    elif operation == 'attend_meeting':
        # create a new record
        result_data = attend_result(input_data)
        dynamo.put_item(**result_data)
        # TODO: Update club members
        return  '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
           '<Response><Message><Body>Response Recorded!</Body></Message></Response>'
    elif operation == 'update':
        # add to an existing result by updating the reps
        # or adding to the message
        result_data = update_result(input_data)
        dynamo.update_item(**result_data)
        # TODO: Update club members
        return '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
           '<Response><Message><Body>Response Updated!</Body></Message></Response>'
    else:
        # The message is unexpected
        return respond(ValueError('What you talking bout willis'))

    operation = event['httpMethod']
    if operation in operations:
        payload = event['queryStringParameters'] if operation == 'GET' else json.loads(event['body'])
        return respond(None, operations[operation](dynamo, payload))
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))