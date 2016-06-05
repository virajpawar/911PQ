#!/usr/bin/env python

import asyncio
import logging
import json
import os
from collections import OrderedDict

import watson_developer_cloud as wdc
import websockets
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger()
stream_hdlr = logging.StreamHandler()
stream_hdlr.setFormatter(
    logging.Formatter(
        '[%(asctime)s] [%(process)d] [%(name)s] [%(levelname)s] '
        '{%(funcName)s:%(lineno)d} %(message)s'))
logger.addHandler(stream_hdlr)
logger.setLevel(logging.INFO)

obj_store = []


def record_call(path):
    os.system('arecord -f cd -t wav -D hw:0,0 -d 5 {}'.format(path))
    logger.info('Recording saved as {}'.format(path))


def transcribe(path):
    with open(path, 'rb') as audio:
        logger.info('Transcribing ...')
        stt = wdc.SpeechToTextV1(
            username='90b022d0-9f21-4e16-b8ab-27c09d20ff07',
            password='RqUOkHKtfnNH')
        response = stt.recognize(
            audio,
            content_type='audio/wav',
            continuous=True)

    chunks = []
    for a in response['results']:
        chunks.append(a['alternatives'][0]['transcript'].strip())

    return ' '.join(chunks)


def classify(message):
    logger.info('Classifying ...')
    nlc = wdc.NaturalLanguageClassifierV1(
        username='7d58e6c7-fe6b-489f-b59e-d592bf21ca64',
        password='wV0NF2qz1DJi')
    try:
        response = nlc.classify('3a84d1x62-nlc-20646', message)
        response = {
            'confidence': response['classes'][0]['confidence'],
            'message': response['text'],
            'priority': response['classes'][0]['class_name'],
        }
    except wdc.WatsonException:
        response = {
            'confidence': None,
            'message': '%EMPTY_MESSAGE',
            'priority': None
        }

    return response


def cluster(event):
    vectorizer = TfidfVectorizer(analyzer='word', stop_words='english')
    messages = [obj['message'] for obj in obj_store] + [event['message']]
    logger.info(messages)
    vectors = vectorizer.fit_transform(messages)
    for i, sim in enumerate(cosine_similarity(vectors[-1], vectors)[0]):
        if i >= len(obj_store):
            break

        if sim >= .8 and len(obj_store) > 0:
            event['incidentID'] = obj_store[i]['incidentID']
            break

    return event


async def producer():
    global obj_store

    input('Press Enter to record a 5 second message ...')
    audio_path = '/tmp/output.wav'
    record_call(audio_path)
    obj = classify(transcribe(audio_path))
    obj.update({
        'callerName': len(obj_store),
        'incidentID': len(obj_store),
    })
    obj = cluster(obj)
    logger.info('Adding event: {}'.format(obj))
    obj_store.append(obj)
    return obj


async def handler(websocket, path):
    while True:
        obj = await producer()
        await websocket.send(json.dumps(obj))
        logger.info('Done\n')


loop = asyncio.get_event_loop()
loop.run_until_complete(websockets.serve(handler, '0.0.0.0', 23456))
loop.run_forever()
