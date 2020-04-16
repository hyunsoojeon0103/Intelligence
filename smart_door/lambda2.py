import json
import boto3

def lambda_handler(event, context):
    faceId = event['faceId']
    nickname = event['nickname']
    phoneNumber = event['phoneNumber']
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('visitors')
    
    res = table.get_item(Key = {'faceId' : faceId})
    if 'Item' in res:
        table.update_item(
            Key = {
                'faceId': faceId,
            },
            UpdateExpression = 'SET nickname =:x, phoneNumber =:y, verified =:z',
            ExpressionAttributeValues = {
                ':x': nickname,
                ':y': phoneNumber,
                ':z': True
            }
        )
    return {'statusCode': 200}

