import requests
import json


def get_name_channel(site, channel):
    url = f'https://api.audioaddict.com/v1/{site}/channels.json'
    try:
        r = requests.get(url)
        channels = r.json()
        for i in channels:
            if i['id'] == int(channel):
                # print(i['name'])
                return i['name']
    except BaseException:
        return []
