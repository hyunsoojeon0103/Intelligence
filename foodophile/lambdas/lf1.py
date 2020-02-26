import json
import boto3
def lambda_handler(event, context):
    #url = 'https://sqs.us-east-1.amazonaws.com/781927886046/myqueue.fifo'
    #response = client.send_message(QueueUrl=url, MessageBody = event)
    #response = client.send_message(QueueUrl=url, MessageBody=json.dumps(event))
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='myqueue')
    res = queue.send_message(MessageBody=json.dumps(event))
    
    return  {
      "dialogAction": {
        "type": "Close",
        "fulfillmentState": "Fulfilled",
        "message": {
            "contentType": "PlainText",
            "content": "You're all set. Expect my suggestions shortly! Have a good day."
        },
      }
    } 
