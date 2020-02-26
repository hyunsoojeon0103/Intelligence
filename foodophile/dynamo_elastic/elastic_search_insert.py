from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import json
import decimal

'''
db_american_new_cuisine.json
db_brazilian_new_cuisine.json
db_chinese_new_cuisine.json
db_french_new_cuisine.json
db_italian_new_cuisine.json
db_korean_new_cuisine.json
db_mexican_new_cuisine.json
'''

host = 'search-restaurant-43cmekj4ukkr63lyajc72ga7gu.us-east-1.es.amazonaws.com' # For example, my-test-domain.us-east-1.es.amazonaws.com
region = 'us-east-1' # e.g. us-west-1

service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

bulk_file = ''

src = open('db_french_new_cuisine.json', 'r')
contents = src.read()
form = "[" + contents.replace('}{', '},\n{') + "]"

json_db = json.loads(form, strict=False, parse_float=decimal.Decimal)
count = 0
try:
    for item in json_db:
        for i in range(50):
            print(count)
            count += 1
            business_id = item['businesses'][i]['id']
            categories = 'French'
            bulk_file += '{ "index" : { "_index" : "restaurants", "_type" : "Restaurant", "_id" : "' + business_id + '" } }\n'
            bulk_file += '{"id": "' + business_id + '" , "cuisine" : "' + categories + '" }\n'
except IndexError:
    print("index out")
        


#print(bulk_file)

# The action_and_metadata portion of the bulk file
#bulk_file += '{ "index" : { "_index" : "restaurants", "_type" : "Restaurant", "_id" : "' + str(id) + '" } }\n'
#bulk_file += '{"id": "' + str(id) + '" + "cuisine" : categories}\n'



es = Elasticsearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)
es.bulk(bulk_file)


