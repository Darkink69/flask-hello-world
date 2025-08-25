import requests
import json
import time


def update_public_folder_settings(token, path, days=7):

    url = "https://cloud-api.yandex.net/v1/disk/public/resources/public-settings"
    expiration_timestamp = int(time.time() + (days * 24 * 60 * 60))

    headers = {
        "Authorization": f"OAuth {token}",
        "Content-Type": "application/json",
    }
    params = {
        "path": path
    }
    payload = {
        "available_until": expiration_timestamp
    }

    try:
        response = requests.patch(url, headers=headers, params=params,
                                  data=json.dumps(payload))

        if response.status_code == 200:
            return True

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

