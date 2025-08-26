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

oauth_token = "y0__xC70devARjblgMg3NzV4xMIZ_XCL_u7KWPy_1nYK9cpmiVNUQ"
days = 7


def get_channel_info(site, channel):
    """Получает всю информацию о канале: название, треки, размер, время загрузки"""
    try:
        name_channel = get_name_channel.get_name_channel(site, channel)
        name_folder = f"difm/{site}/{channel}_{name_channel}/"

        # Создаем папку если не существует
        exists = check_name_folder.check_folder_exists(oauth_token, name_folder)
        if not exists:
            res = make_folder.make_y_folder(oauth_token, name_folder)
            if res:
                print(f"Папка '{name_folder}' создана на Яндекс.Диске")

        # Получаем публичную ссылку
        public_link = publish_folder.publish_and_get_public_link(oauth_token,
                                                                 name_folder)
        if public_link:
            print(f"Публичная ссылка: {public_link}")
            res = set_publish_link_expiry.update_public_folder_settings(
                oauth_token, name_folder, days)
            if res:
                print(f"Ссылка будет действовать {days} дней.")
        else:
            print("Не удалось получить публичную ссылку.")
            return {'error': 'Не удалось получить публичную ссылку'}

        # Получаем треки
        url_ch = f'https://qh8bsvaksadb2kj9.public.blob.vercel-storage.com/{site}/db_{site}_full_{channel}_light.json'
        tracks = get_json_channel.get_json_channel_tracks(url_ch)

        # Рассчитываем общий размер и время загрузки
        total_size = 0
        for track in tracks:
            total_size += track['size']

        total_size_gb = round(total_size / 1024 / 1024 / 1024, 2)
        estimated_time_hours = round(len(tracks) * 15 / 60 / 60,
                                     1)  # 15 секунд на трек

        print(f"Всего на канале {name_channel} - {len(tracks)} трека(ов)")
        print(
            f"Примерное время загрузки всех файлов - {estimated_time_hours} часа(ов)")
        print(f'Общий размер всех файлов - {total_size_gb} ГБайт')

        return {
            'name_channel': name_channel,
            'public_link': public_link,
            'tracks': tracks,
            'total_tracks': len(tracks),
            'total_size_gb': total_size_gb,
            'estimated_time_hours': estimated_time_hours
        }

    except Exception as e:
        print(f"Ошибка при получении информации о канале: {e}")
        return {'error': str(e)}


def get_public_link_prepare(site, channel):
    """Подготовительная работа: создание папки и получение публичной ссылки"""
    info = get_channel_info(site, channel)
    return info['public_link'] if 'public_link' in info else None


def upload_single_track(site, channel, track, public_link):
    """Загрузка одного трека"""
    try:
        name_channel = get_name_channel.get_name_channel(site, channel)
        name_folder = f"difm/{site}/{channel}_{name_channel}/"

        data_link = get_random_acсess.get_access_data()
        file_url = 'https:' + track['url'] + '?' + data_link
        filename = track['track'] + '.mp3'

        res = upload_url_file.upload_file_to_yandex_disk_from_url(
            oauth_token,
            name_folder,
            filename,
            file_url
        )

        # Небольшая пауза между загрузками
        time.sleep(random.randint(10, 20))

        return {'success': True, 'filename': filename, 'result': res}

    except Exception as e:
        return {'success': False, 'filename': track['track'], 'error': str(e)}


def get_public_link(site, channel):
    """Старая функция для обратной совместимости"""
    info = get_channel_info(site, channel)

    if 'error' in info:
        return f"Ошибка: {info['error']}"

    return f"Канал: {info['name_channel']}, Треков: {info['total_tracks']}, Размер: {info['total_size_gb']} GB, Время: {info['estimated_time_hours']} часов. Ссылка: {info['public_link']}"


# Экспортируем модули для использования в index.py
get_json_channel = get_json_channel