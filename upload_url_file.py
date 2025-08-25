import requests
import time


def upload_file_to_yandex_disk_from_url(oauth_token, name_folder, filename, file_url):

    yandex_path = name_folder + filename

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
            # print("Файл поставлен в очередь на загрузку")
            # 3. Проверяем статус загрузки
            status_url = response.json().get("href")
            # return check_upload_status(headers, status_url, yandex_path)
        else:
            print(f"Неожиданный ответ: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке файла: {e}")
        return None

    return filename, '- ok'



