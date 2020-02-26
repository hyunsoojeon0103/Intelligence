import requests
import json

api_key = 'IcwwCTjZwHsJaOcm1Neg4ajvCWXIN0EEVJ2yUtDKDMqBrNUxRwsjVEVkiTnFaBL7l1cEc7Pk6b-qO3fqLKGZBAVpRYBRQwdRVe6PuqUrBqSr2jxr8uhiF8PnC5pMXnYx'
endpoint = 'https://api.yelp.com/v3/businesses/search'
headers = {'Authorization': 'bearer {}'.format(api_key)}


for offset in range(0, 1000, 50):
    param = {'term': 'American restaurants',
             'location': 'manhattan',
             'limit': 50,
             'offset': offset}

    response = requests.get(url=endpoint, params=param, headers=headers) 

    if response.status_code == 200:
        data = response.json()
        with open("db_american_new_cuisine.json", 'a') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(offset)
    else:
        print("error code returned")
        break

'''
f = open("chinese_cuisine.json", "a")
f.write(data)
f.close()
'''
