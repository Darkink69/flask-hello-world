import get_json_channel
import get_random_acсess
import upload_url_file
import make_folder
import get_name_channel
import check_name_folder
import publish_folder
import set_publish_link_expiry
import time
import random

oauth_token = "y0__xC70devARjblgMg3NzV4xMIZ_XCL_u7KWPy_1nYK9cpmiVNUQ"  # Ваш OAuth-токен

# site = 'di'
# channel = 6

days = 7

def upload_mp3(site, channel):
    url_ch = f'https://qh8bsvaksadb2kj9.public.blob.vercel-storage.com/{site}/db_{site}_full_{channel}_light.json'

    name_channel = get_name_channel.get_name_channel(site, channel)
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


    tracks = get_json_channel.get_json_channel_tracks(url_ch)
    # print(tracks)
    size = 0
    print(f"Всего на канале {name_channel} - {len(tracks)} трека(ов)")
    print(f"Примерное время загрузки всех файлов - {round(len(tracks) * 10 / 60 / 60, 1)} часа(ов)")
    for track in tracks:
        size += track['size']
    print('Общий размер всех файлов -', round(size / 1024 / 1024 / 1024, 2), 'ГБайт')

    data_link = get_random_acсess.get_access_data()

    tracks = tracks[:5]
    for track in tracks:
        file_url = 'https:' + track['url'] + '?' + data_link
        filename = track['track'] + '.mp3'
        res = upload_url_file.upload_file_to_yandex_disk_from_url(oauth_token, name_folder, filename, file_url)
        print(res)

        time.sleep(random.randint(10, 20))

    return f"Загрузка {site} - {name_channel} завершена."