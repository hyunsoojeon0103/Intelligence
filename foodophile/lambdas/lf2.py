import boto3
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from boto3.dynamodb.conditions import Key, Attr
import random


def lambda_handler(event, context):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='myqueue')
    
    host = 'search-restaurant-43cmekj4ukkr63lyajc72ga7gu.us-east-1.es.amazonaws.com' # For example, my-test-domain.us-east-1.es.amazonaws.com
    region = 'us-east-1' # e.g. us-west-1
    session = boto3.Session(
            region_name = "us-east-1"
        )
        
    service = 'es'
    credentials = session.get_credentials()
    awsauth = AWS4Auth(credentials.access_key,
            credentials.secret_key,
            region, service,
            session_token=credentials.token
        )
    
    es = Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    esinfo = es.info()
    
    message = None
    messages = queue.receive_messages()
    
    if len(messages) == 0:
        return {
            'statusCode': 200,
            'body': "empty queue"
        }
    else:
        message = messages[0]
        
    body = json.loads(message.body)
    
    message.delete()

    CuisineType = body['currentIntent']['slots']['CuisineType']
    Phone_Number = body['currentIntent']['slots']['PhoneNumber']
    numPeople = body['currentIntent']['slots']['NumberOfPeople']
    time = body['currentIntent']['slots']['Time']
    Date = body['currentIntent']['slots']['Date']
    
    response_msg = "Hello! Here are " + CuisineType + " restaurant suggestions for " + \
        numPeople + " people on " + Date + " at "+ time + " "


    es.indices.refresh(index="restaurants")
    total = es.count(q= CuisineType)
    if total['count'] == 0:
        return {
            'statusCode': 200,
            'Type': CuisineType,
            'body': "cannot find the resturant type"
        }
        
        
    rand_offset=random.choice(range(0, total['count']))  # Generate random offset to get random resturants 
    
    search_body = {
        "query": {
            "simple_query_string": {
                "query":  CuisineType
            }
        },

        "size": 3,
        "from": rand_offset
    }

    # body=search_body
    res = es.search(body=search_body)
    
    
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table('yelp-restaurants')
   
    for i in range(len(res["hits"]["hits"])): 
        result_id = res["hits"]["hits"][i]["_id"]
        dynamodb_response = table.query(
            KeyConditionExpression=Key('business_id').eq(result_id)
        )
        zipcode = dynamodb_response['Items'][0]["zipcode"]
        rating = dynamodb_response['Items'][0]["rating"]
        categories = dynamodb_response['Items'][0]["categories"]
        address = dynamodb_response['Items'][0]["address"]
        name = dynamodb_response['Items'][0]["name"]
        
        response_msg += str(i+1) +". "+ name + ", located at " + address + " " + \
            zipcode + ", "
        
        # We specify to have 3 results, just in case. 
        if i == 2:
            break 
    
    response_msg += "Enjoy your meal!"
    
    sns_client = boto3.client('sns')
    
    if Phone_Number[0] != "1":
        Phone_Number = "1"+Phone_Number
    
    response = sns_client.publish(
        PhoneNumber= "+"+Phone_Number,
        Message=response_msg
    )
    
    return {
        'statusCode': 200, 
        'body': len(res["hits"]["hits"]),
        'db size':total,
        'phoneNumber': Phone_Number,
        'response_msg':  response_msg
    }
    

