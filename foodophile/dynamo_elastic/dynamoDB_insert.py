import json
import boto3
from datetime import datetime
import decimal

def check_empty(word):
    if word:
        return word
    else:
        return "unknown"


if __name__ == "__main__":
    #connect dynamodb on cloud
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('yelp-restaurants')

    #all cuisine json info loaded from src
    src = open('db_mexican_new_cuisine.json', 'r')
    contents = src.read()
    form = "[" + contents.replace('}{', '},\n{') + "]"

    json_db = json.loads(form, strict=False, parse_float=decimal.Decimal)
    count = 0
    for item in json_db:
        for i in range(50):
            print(count)
            count += 1
            addr = item['businesses'][i]['location']["address1"]
            if(item['businesses'][i]['location']["address2"]):
                addr += item['businesses'][i]['location']["address2"]
            if(item['businesses'][i]['location']["address3"]):
                addr += item['businesses'][i]['location']["address3"]

            business_id = item['businesses'][i]['id']
            time_stamp = str(datetime.now())
            name = item['businesses'][i]['name']
            coordinates = item['businesses'][i]["coordinates"]
            review_count = item['businesses'][i]['review_count']
            rating =  item['businesses'][i]['rating']

            it = {
                    'business_id': check_empty(business_id),
                    'insertedAtTimestamp': time_stamp,
                    'name': check_empty(name),
                    'categories': 'Mexican',
                    'address': check_empty(addr),
                    'coordinates': check_empty(coordinates), 
                    'review_count': check_empty(review_count),
                    'rating': check_empty(rating),
                    'zipcode': check_empty(item['businesses'][i]['location']['zip_code'])
            }

            table.put_item( Item = it )
            '''
            print(datetime.now())
            print(item['businesses'][i]['id'])
            print(item['businesses'][i]['name'])
            addr = item['businesses'][i]['location']["address1"]
            if(item['businesses'][i]['location']["address2"]):
                addr += item['businesses'][i]['location']["address2"]
            if(item['businesses'][i]['location']["address3"]):
                addr += item['businesses'][i]['location']["address3"]
            print(addr)
            print (item['businesses'][i]['location']["zip_code"])
            print(item['businesses'][i]["coordinates"])
            print(item['businesses'][i]['review_count'])
            print(item['businesses'][i]['rating'])
            print("\n")
            '''