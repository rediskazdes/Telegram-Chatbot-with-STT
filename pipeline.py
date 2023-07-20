import re
import csv
import pymongo
import pandas as pd
import os

parent = r'C:\Users\dbulygin\Dropbox\pythonProject\recordings'

ids = os.listdir(parent)

#processed_profiles = open(r"C:\Users\dbulygin\Dropbox\pythonProject\processed_profiles.txt", "r")
#processed_profiles = processed_profiles.read()
#processed_profiles = processed_profiles.replace('\n', ' ').split(".")

#setA = set(ids)
#setB = set(processed_profiles)

#ids = list(setA.difference(setB))
#print(ids[0])

column_names = ["Prolific ID", "File", "Question", "Transcription"]

if not os.path.exists(r'C:\Users\dbulygin\Dropbox\pythonProject\transcripts.csv'):
    df_final = pd.DataFrame(columns=column_names)
    print('new')
else:
    df_final = pd.read_csv(r'C:\Users\dbulygin\Dropbox\pythonProject\transcripts.csv')
    processed = df_final['Prolific ID'].unique().tolist()
    setA = set(ids)
    setB = set(processed)
    ids = list(setA.difference(setB))
    print('old')
    print(ids)

for id in ids:
    files = os.listdir(os.path.join(parent, id))
    regex = re.compile(r'Q\d_')
    files = [i for i in files if regex.match(i)]

    df = pd.DataFrame(columns=column_names)
    for file in files:
        final_file = os.path.join(parent,id,file)
        print(file)
        print(final_file)
        ############### SPEECH TO TEXT #####################
        from google.cloud import speech_v1 as speech
        import io, os, subprocess, json
        def transcribe_file(speech_file):
            """Transcribe the given audio file."""

            client = speech.SpeechClient.from_service_account_json("credentials.json")

            with io.open(speech_file, "rb") as audio_file:
                content = audio_file.read()

            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
                sample_rate_hertz=48000,
                language_code="en-US",
                #alternativeLanguageCodes= ['en_UK'],
                model='latest_long',
                enable_automatic_punctuation=True
            )

            response = client.recognize(config=config, audio=audio)

            # Each result is for a consecutive portion of the audio. Iterate through
            # them to get the transcripts for the entire audio file.
            transc = ''
            for result in response.results:
                # The first alternative is the most likely one for this portion.
                 transc = transc + str(result.alternatives[0].transcript)
            return transc

        transcription = transcribe_file(final_file)

        print(transcription)
        Q = re.search(r'Q\d_', file).group(0)
        Q = re.sub('_', '', Q)

        d = {'Prolific ID': pd.Series(id),
             'File': pd.Series(file),
             'Question': pd.Series([Q]),
             'Transcription':pd.Series(transcription)}
        print(d)
        d = pd.DataFrame(data = d)
        df = df.append(d)

    #processed_profiles.append(id)

    #with open(r'C:\Users\dbulygin\Dropbox\pythonProject\processed_profiles.txt', 'w') as fp:
    #    for item in processed_profiles:
    #        # write each item on a new line
    #        fp.write("%s\n" % item)
    #    print('Done')

    df_final = df_final.append(df)
    df_final.to_csv(r'C:\Users\dbulygin\Dropbox\pythonProject\transcripts.csv', encoding='utf-8')

#import itertools as it
#t=(('1','a'), ('1','A'), ('2','b'), ('2','B'), ('3','c'),('3', 'C'))

#{k:tuple(x[1] for x in v) for k,v in it.groupby(sorted(t), key=lambda x: x[0])}

#print(transcript)






#test_client = pymongo.MongoClient('mongodb://localhost:27017/')
#db_name = 'interviews'
#coll_name = 'testing'

#db = test_client[db_name]
#collection = db[coll_name]

#result = collection.find({'type':'voice'})
#voices = pd.DataFrame(result)
#print(voices)

#ids = list(collection.find({'type':'voice'}).distinct('Prolific ID'))
#print(ids[0])

#files = list(collection.find_one({'type':'voice','Prolific ID': ids[0]}))
             #,{'Q1':1,'Q2':1,'Q3':1,'Q4':1,'_id':False}))
#print(files)

#def flatten(l):
#    return [item for sublist in l for item in sublist]

#files = [x.replace(' ','_') for x in files]
#files = flatten(files)
#print(files)

#for recs in result:
#    print(recs)

#print(voices.columns)