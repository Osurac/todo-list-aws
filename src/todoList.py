import os
import boto3
import time
import uuid
import json
import functools
from botocore.exceptions import ClientError

ACCESS_KEY = "ASIAWLNG7FL2WL3WXTZN"
SECRET_KEY = "JYNDY+jg2pNeBvfTqYbDbxYHFTmVxFH9XUkB+FW1"
SESSION_TOKEN = ("FwoGZXIvYXdzEKL//////////wEaDH953LPgFAc7e1V9bCLRAaDJLhzZY"
                 "MJCTxhffIRi/ay876kpzgFdEEO+D9eeNjGuinUYW+D2qQ4Op0cRJp/6rj7"
                 "HOkC1DPpSFIx32uJzhPBYjznQuwFIRuaG/8WJ0cqnhbA1N20FojD5q/mK7"
                 "ll3zDLn+p3XF1HhXjFLEypXTR8Q7Kb1Y3RqQIXQx+MJBBZ4W8JIgklERwik"
                 "omOIiYpLY6xXftnRUDpDvC4kqlvR6r6i+jAvmkZ6UT8Mkbf9jmoUPrQMEGgI"
                 "c2SsrvcyFQvKkv07jORXMf/X08KkBgUXXiW8KNeY+p4GMi2tA3ynEoKPNOc8"
                 "THQOrCYQ5GuTPHRW3Q9yUTsAteYEA98sRX+P7NbQ6RLzatA=")


def get_table(dynamodb=None):
    if not dynamodb:
        URL = os.environ['ENDPOINT_OVERRIDE']
        if URL:
            print('URL dynamoDB:'+URL)
            boto3.client = functools.partial(boto3.client, endpoint_url=URL)
            boto3.resource = functools.partial(boto3.resource,
                                               endpoint_url=URL)
        dynamodb = boto3.resource("dynamodb")
    # fetch todo from the database
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    return table


def get_item(key, dynamodb=None):
    table = get_table(dynamodb)
    try:
        result = table.get_item(
            Key={
                'id': key
            }
        )

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print('Result getItem:'+str(result))
        if 'Item' in result:
            return result['Item']


def get_items(dynamodb=None):
    table = get_table(dynamodb)
    # fetch todo from the database
    result = table.scan()
    return result['Items']


def put_item(text, dynamodb=None):
    table = get_table(dynamodb)
    timestamp = str(time.time())
    print('Table name:' + table.name)
    item = {
        'id': str(uuid.uuid1()),
        'text': text,
        'checked': False,
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }
    try:
        # write the todo to the database
        table.put_item(Item=item)
        # create a response
        response = {
            "statusCode": 200,
            "body": json.dumps(item)
        }

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response


def update_item(key, text, checked, dynamodb=None):
    table = get_table(dynamodb)
    timestamp = int(time.time() * 1000)
    # update the todo in the database
    try:
        result = table.update_item(
            Key={
                'id': key
            },
            ExpressionAttributeNames={
              '#todo_text': 'text',
            },
            ExpressionAttributeValues={
              ':text': text,
              ':checked': checked,
              ':updatedAt': timestamp,
            },
            UpdateExpression='SET #todo_text = :text, '
                             'checked = :checked, '
                             'updatedAt = :updatedAt',
            ReturnValues='ALL_NEW',
        )

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return result['Attributes']


def delete_item(key, dynamodb=None):
    table = get_table(dynamodb)
    # delete the todo from the database
    try:
        table.delete_item(
            Key={
                'id': key
            }
        )

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return


def create_todo_table(dynamodb):
    # For unit testing
    tableName = os.environ['DYNAMODB_TABLE']
    print('Creating Table with name:' + tableName)
    table = dynamodb.create_table(
        TableName=tableName,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )

    # Wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName=tableName)
    if (table.table_status != 'ACTIVE'):
        raise AssertionError()

    return table


def translate_item(text, language, dynamodb=None):
    client = boto3.client(service_name='translate',
                          use_ssl=True,
                          aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY,
                          aws_session_token=SESSION_TOKEN,
                          region_name='us-east-1')
    try:
        res = client.translate_text(
            Text=text, SourceLanguageCode="auto", TargetLanguageCode=language)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        translation = res.get('TranslatedText')
        return translation
