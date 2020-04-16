import json
import boto3 
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    #get the passcode input from the visitor
    #OTP = "".join(str(event).split()).replace("'","")
    OTP = event['otp']
    
    #connect to db and search for the passcode
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('passcodes')
    table2 = dynamodb.Table('visitors')
    res = table.get_item(Key = {'passcode' : OTP})
    message = ""
    # create personalized greeting
    if 'Item' in res:
        print("found")
        item = res['Item']
        faceId = item['faceId']
        resV = table2.get_item(Key = {'faceId' :faceId })
        name = resV['Item']['nickname']
        message = 'Please enter the door, {}!'.format(name)
    else:
        message = 'permission denied!'
        
    return message
