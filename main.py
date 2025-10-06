import json

from Cython import returns

import get_json_channel
import get_random_acсess
import upload_url_file
import make_folder
import get_name_channel
import check_name_folder
import publish_folder
import set_publish_link_expiry
import update_txt_order
import time
import random

oauth_token = "y0__xC70devARjblgMg3NzV4xMIZ_XCL_u7KWPy_1nYK9cpmiVNUQ"  # Ваш OAuth-токен

# site = 'di'
# channel = 6
# https://qh8bsvaksadb2kj9.public.blob.vercel-storage.com/classicalradio/db_classicalradio_full_360_premium_light.json

days = 7

def upload_mp3(site, channel, order):
    url_ch = f'https://qh8bsvaksadb2kj9.public.blob.vercel-storage.com/{site}/db_{site}_full_{channel}_premium_light.json'

    name_channel = get_name_channel.get_name_channel(site, channel)
    # name_folder = f"difm/{site}/{channel}_Classic EuroDisco/"
    name_folder = f"difm/{site}/{channel}_{name_channel}/"
    exists = check_name_folder.check_folder_exists(oauth_token, name_folder)
    if exists:
        print(f"Папка '{name_folder}' уже есть на Яндекс.Диске")
    else:
        res = make_folder.make_y_folder(oauth_token, name_folder)
        if res:
            print(f"Папка '{name_folder}' создана на Яндекс.Диске")



    public_link = publish_folder.publish_and_get_public_link(oauth_token, name_folder)
    if public_link:
        print(f"Публичная ссылка: {public_link}")
        res = set_publish_link_expiry.update_public_folder_settings(oauth_token, name_folder, days)
        if res:
            print(f"Ссылка будет действовать {days} дней.")
    else:
        print("Не удалось получить публичную ссылку.")

    # update_txt_order.update_channel_in_file(f"../orders/{order}.txt", name_channel,
    #                        public_link)

    tracks = get_json_channel.get_json_channel_tracks(url_ch)

    current_channels = json.load(open(f'orders/{order}.json', "r", encoding='utf-8'))
    # current_channels = json.load(open(f'../orders/{order}.json', "r", encoding='utf-8'))
    # print(current_channels)

    # Проверяем, где остановилась закачка и корректируем
    for current in current_channels:
        if current['id'] == int(channel) and not current['isDownloaded']:
            # print(current['id'])
            for index, track in enumerate(tracks):
                # if track['id'] == 3107684:
                if track['id'] == current['lastId']:
                    tracks = tracks[index + 1:]


    # print(tracks)
    size = 0
    print(f"Всего на канале {name_channel} - {len(tracks)} трека(ов)")
    print(f"Примерное время загрузки всех файлов - {round(len(tracks) * 20 / 60 / 60, 1)} часа(ов)")
    for track in tracks:
        size += track['size']
    print('Общий размер всех файлов -', round(size / 1024 / 1024 / 1024, 2), 'ГБайт')

    data_link = get_random_acсess.get_access_data()

    # tracks = tracks[:5] # Загружать только первые 5
    for index, track in enumerate(tracks):
        print(f'Трек --------- {index + 1}/{len(tracks)} ---------')
        # file_url = 'https:' + track['url'] + '?' + 'purpose=playback&audio_token=615841863e5533f627fa26bd6e921776&network=di&device=chrome_140_windows_10&exp=2025-10-01T07:18:38Z&auth=733bcaf9440f3711c5d3ccaae492adf50ccc0182'
        file_url = 'https:' + track['url'] + '?' + data_link
        filename = track['track'] + '.mp3'
        res = upload_url_file.upload_file_to_yandex_disk_from_url(oauth_token, name_folder, filename, file_url)
        print(res)

        current_channels = json.load(
            open(f'orders/{order}.json', "r", encoding='utf-8'))
            # open(f'../orders/{order}.json', "r", encoding='utf-8'))

        # Записываем последний id скачанного трека
        for current in current_channels:
            if current['id'] == int(channel) and not current['isDownloaded']:
                current['lastId'] = track['id']
                with open(f'orders/{order}.json', 'w') as f:
                # with open(f'../orders/{order}.json', 'w') as f:
                    json.dump(current_channels, f, indent=2)

        time.sleep(random.randint(10, 20))

    return f"Загрузка {site} - {name_channel} завершена."

# upload_mp3('di', 183, 'oeljot')


# загрузка по одному, должна быть на сервере
def upload_one_mp3(site, channel, id_track):
    print(site, channel, id_track, '!!!')
    return site, channel, id_track