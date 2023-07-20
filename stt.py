from google.cloud import speech_v1 as speech
import io, os, subprocess, json


def transcribe_file(speech_file):
    """Transcribe the given audio file."""

    client = speech.SpeechClient.from_service_account_json("credentials.json")

    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.mp3,
        sample_rate_hertz=48000,
        language_code="en-US",
        #alternativeLanguageCodes= ['en_UK'],
        model='latest_long',
        enableAutomaticPunctuation = True
    )

    response = client.recognize(config=config, audio=audio)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    transc = ''
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        transc = transc + str(result.alternatives[0].transcript)

    with open('test.txt', 'w') as f:
        f.write(transc)

    return transc


#transcribe_file(r'C:\Users\dbulygin\Dropbox\pythonProject\recordings\filename.ogg')