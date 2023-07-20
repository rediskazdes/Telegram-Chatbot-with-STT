import pymongo

test_client = pymongo.MongoClient('mongodb://localhost:27017/')

db_name = 'interviews'
coll_name = 'testing'

db = test_client[db_name]
collection = db[coll_name]

#import datetime
#post = {"Prolific ID": "Mike",
#        "answers": [],
#        "type": "text"}

#datetime.datetime.utcnow()

result = collection.find({'type':'voice'})

import pandas as pd

voices = pd.DataFrame(result)

for recs in result:
    print(recs)


print(voices.head(6))

print(voices.keys())

responses = voices[['Q1','Q2','Q3','Q4','Q5']]
print(responses['Q1'])

responses.to_csv('test.csv')

# Let's get all voice responses

'C:\\Users\\dbulygin\\Dropbox\\pythonProject\\recordings\\I4qiyhMZVdXg9EcPrGPLjHjw\\Q1 20220826 190146.ogg'