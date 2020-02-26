import json
import boto3
def lambda_handler(event, context):
    client = boto3.client('lex-runtime')
    response = client.post_text(botName = 'FoodBot', botAlias ='FoodBotBot', userId ='hj2509', inputText=event['messages'])
    return {
        'statusCode': 200,
        'body': json.dumps(response['message'])
    }
