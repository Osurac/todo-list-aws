import json
import todoList


def translate(event, context):
    try:
        item = todoList.get_item(event['pathParameters']['id'])
        translation = todoList.translate_item(
            item['text'], event['pathParameters']['language']
            )
        return {
            "statusCode": 200,
            "body": json.dumps(translation)
            }
    except KeyError as e:
        return {
            "statusCode": 404,
            "body": str(e)
            }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
            }
