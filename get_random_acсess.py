import requests
import json
from fake_useragent import UserAgent
import random
import time
import os

ua = UserAgent()

sites = ['di', 'rockradio', 'radiotunes', 'jazzradio', 'classicalradio', 'zenradio']

def get_access_data():
    link = f'https://qh8bsvaksadb2kj9.public.blob.vercel-storage.com/audio/audio.json'
    headers = {"User-Agent": ua.random}
    r = requests.get(link, headers=headers)
    tokens = r.json()
    # print('Всего токенов -', len(tokens))
    for i in range(25):
        print('Попытка получения токена -', i + 1)
        id = random.randint(1, 15)
        ts = str(int(time.time() * 1000))
        audio_token = random.choice(tokens) + '&_=' + ts
        # audio_token = random.choice(tokens)

        # audio_token = f'958b3ee79e1b5cac40b80a71a1bf463b&_={ts}'
        # print(audio_token)

        link_hidden = f'https://api.audioaddict.com/v1/{sites[0]}/routines/channel/{id}?tune_in=true&audio_token={audio_token}'
        print(link_hidden)
        headers = {"User-Agent": ua.random}
        try:
            r = requests.get(link_hidden, headers=headers)
            group_tracks = r.json()
            data_link = (group_tracks["tracks"][0]['content']['assets'][0]['url']).split('?')[1]
            # print(data_link)
            return data_link
        except BaseException:
            print('no access')
            time.sleep(random.randint(2, 5))

