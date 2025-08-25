import requests


def check_folder_exists(oauth_token, folder_name):

    url = "https://cloud-api.yandex.net/v1/disk/resources"

    headers = {
        "Authorization": f"OAuth {oauth_token}"
    }

    params = {
        "path": folder_name
    }

    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return True  # Папка существует
        elif response.status_code == 404:
            return False  # Папка не найдена
        else:
            print(
                f"Ошибка при проверке папки. Код статуса: {response.status_code}")
            print(f"Ответ сервера: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API Яндекс.Диска: {e}")
        return False


