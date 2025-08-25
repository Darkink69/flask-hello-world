import requests
import time


def publish_and_get_public_link(oauth_token, path):
    # Шаг 1: Публикуем ресурс
    publish_url = "https://cloud-api.yandex.net/v1/disk/resources/publish"
    headers = {
        "Authorization": f"OAuth {oauth_token}",
        "Content-Type": "application/json"
    }
    params = {
        "path": path
    }

    try:
        # Запрос на публикацию
        response = requests.put(publish_url, headers=headers, params=params)
        response.raise_for_status()

        # Ждем немного, чтобы Яндекс успел обработать запрос
        time.sleep(2)

        # Шаг 2: Получаем информацию о ресурсе (включая публичную ссылку)
        info_url = "https://cloud-api.yandex.net/v1/disk/resources"
        params = {
            "path": path,
            "fields": "public_url"  # Запрашиваем поле с публичной ссылкой
        }

        response = requests.get(info_url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        public_url = data.get("public_url")

        if public_url:
            # Преобразуем ссылку в желаемый формат (если нужно)
            # Из https://yadi.sk/d/... в https://disk.yandex.ru/d/...
            public_url = public_url.replace("yadi.sk", "disk.yandex.ru")
            return public_url
        else:
            print("Ресурс опубликован, но публичная ссылка не найдена.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при работе с API Яндекс.Диска: {e}")
        return None


