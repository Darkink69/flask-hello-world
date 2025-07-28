import requests
import time


def upload_file_to_yandex_disk_from_url(filename):
    oauth_token = "y0__xC70devARjblgMg3NzV4xMIZ_XCL_u7KWPy_1nYK9cpmiVNUQ"  # Ваш OAuth-токен
    file_url = "https://content.audioaddict.com/prd/4/5/4/5/0/6fee5ff22576794e9399724688efb2b0799.mp3?purpose=playback&audio_token=615841863e5533f627fa26bd6e921776&network=di&device=chrome_113_linux&exp=2025-07-29T03:51:30Z&auth=d2219edf340168ae1948fcc95dcb0ea831209406"  # Ссылка на файл в интернете
    yandex_path = "difm/di/" + filename

    print(filename)
    print(yandex_path)

    # 1. Получаем URL для загрузки
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"

    headers = {
        "Authorization": f"OAuth {oauth_token}",
        "Content-Type": "application/json"
    }

    params = {
        "url": file_url,
        "path": yandex_path,
        "disable_redirects": "true"  # Важно для внешних ссылок
    }

    try:
        # 2. Отправляем POST-запрос для начала загрузки
        response = requests.post(upload_url, headers=headers, params=params)
        response.raise_for_status()

        if response.status_code == 202:
            print("Файл поставлен в очередь на загрузку")
            # 3. Проверяем статус загрузки
            status_url = response.json().get("href")
            # return check_upload_status(headers, status_url, yandex_path)
        else:
            print(f"Неожиданный ответ: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке файла: {e}")
        return None

    return 'ok'



