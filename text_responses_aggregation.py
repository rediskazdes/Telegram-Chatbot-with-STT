import pymongo

test_client = pymongo.MongoClient('mongodb://localhost:27017/')

db_name = 'interviews'
coll_name = 'testing'

db = test_client[db_name]
collection = db[coll_name]

text_responses = collection.find({ "type": {"$ne": "voice"}})

import pandas as pd
voices = pd.DataFrame(text_responses)

test = voices[['Prolific ID', 'Q1','Q2','Q3','Q4']]


test1 = pd.melt(test,id_vars=['Prolific ID'],value_vars=['Q1','Q2','Q3','Q4'])
print(test1)

test1['File'] = 'typed responses'
print(test1)

test1 = test1.rename(columns={"variable": "Question", "value": "Transcription"})

print(test1.columns)

test1.to_csv(r'C:\Users\dbulygin\Dropbox\pythonProject\typed_responses.csv', encoding='utf-8')

print(test)
