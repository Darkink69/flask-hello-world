import requests
import json


def get_name_channel(site, id_channel):
    url = f'https://api.audioaddict.com/v1/{site}/channels.json'
    try:
        r = requests.get(url)
        channels = r.json()
        for channel in channels:
            if channel['id'] == id_channel:
                # print(channel['id'])
                return channel['name']
    except BaseException:
        return []
