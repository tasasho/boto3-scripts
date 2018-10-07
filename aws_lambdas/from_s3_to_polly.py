# coding: utf-8
import boto3
import json
import re
import time
import urllib
from boto3 import Session
from contextlib import closing

session = Session(region_name="ap-northeast-1")
polly = session.client("polly")
s3 = boto3.resource('s3')
audio_file_prefix = "mp3/"


def lambda_handler(event, context):
    try:
        print("Loading function")
        s3_bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        text_file_key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"], encoding="utf8")
        object_content = get_content_from_s3(s3_bucket_name, text_file_key)
        print("Bucket: " + s3_bucket_name)
        print("Text file key: " + text_file_key)

        polly_stream = polly.synthesize_speech(
            Text=object_content,
            OutputFormat="mp3",
            VoiceId="Mizuki"
        )

        audio_file_key = audio_file_prefix + re.sub(r'.*/', '', text_file_key).replace('.txt', '.mp3')
        print("Audio file key: " + audio_file_key)

        put_audio_file_to_s3(s3_bucket_name, audio_file_key, polly_stream)
        print("Complete converting text-file to audio-file")

    except Exception as e:
        print(e)

def get_content_from_s3(s3_bucket_name, text_file_key):
    target_object = s3.Object(s3_bucket_name, text_file_key)
    response = target_object.get()
    return response["Body"].read().decode('utf-8')

def put_audio_file_to_s3(s3_bucket_name, audio_file_key, polly_stream):
    bucket = s3.Bucket(s3_bucket_name)
    with closing(polly_stream["AudioStream"]) as stream:
        bucket.put_object(
            Key=audio_file_key,
            Body=stream.read()
        )