import requests

def make_y_folder(oauth_token, name_folder):
    url = f'https://cloud-api.yandex.net/v1/disk/resources?path={name_folder}'
    headers = {
        "Authorization": f"OAuth {oauth_token}"
    }

    try:
        response = requests.put(url, headers=headers)
        response.raise_for_status()  # Проверяем на ошибки HTTP
        return True


    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API Яндекс.Диска: {e}")
        print(f"Папка {name_folder} НЕ СОЗДАНА")
        return None
