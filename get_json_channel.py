import requests
import json


def get_json_channel_tracks(url_ch):
    try:
        r = requests.get(url_ch)
        tracks = r.json()
        return tracks
    except BaseException:
        return []

