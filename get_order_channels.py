import requests
import json

from js2py.base import false


def process_channels(file):
    # Читаем названия каналов из файла
    with open(f'../orders/{file}.txt', 'r') as f:
        channels = [line.strip() for line in f if line.strip()]

    # Загружаем данные с API
    response = requests.get(
        'https://qh8bsvaksadb2kj9.public.blob.vercel-storage.com/audio/all_radio_data.json'
    )
    radio_data = response.json()

    # Ищем и сохраняем совпадения
    result = []
    for channel in channels:
        for item in radio_data:
            if item['name'] == channel:
                item['lastId'] = 0
                item['isDownloaded'] = False
                result.append(item)
                break

    # Сохраняем результат
    with open(f'../orders/{file}.json', 'w') as f:
        json.dump(result, f, indent=2)

    return f'Файл {file}.json создан'


# https://qh8bsvaksadb2kj9.public.blob.vercel-storage.com/audio/audio_x.json
# process_channels()