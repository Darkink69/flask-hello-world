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
import redis_set

oauth_token = "y0__xC70devARjblgMg3NzV4xMIZ_XCL_u7KWPy_1nYK9cpmiVNUQ"
days = 7


def upload_single_track(session_id, track, name_folder, data_link):
    """Загружает один трек и обновляет статус в Redis"""
    try:
        file_url = 'https:' + track['url'] + '?' + data_link
        filename = track['track'] + '.mp3'

        print(f"Загрузка: {filename}")
        res = upload_url_file.upload_file_to_yandex_disk_from_url(oauth_token,
                                                                  name_folder,
                                                                  filename,
                                                                  file_url)

        if "успешно" in res.lower() or "success" in res.lower():
            redis_set.update_track_status(session_id, track['id'], True)
            return {"success": True, "message": res}
        else:
            redis_set.update_track_status(session_id, track['id'], False, res)
            return {"success": False, "message": res}

    except Exception as e:
        error_msg = f"Ошибка при загрузке: {str(e)}"
        redis_set.update_track_status(session_id, track['id'], False, error_msg)
        return {"success": False, "message": error_msg}


def upload_mp3(site, channel):
    """Основная функция загрузки с поддержкой сессий"""
    # Инициализируем сессию загрузки
    session_info = redis_set.initialize_upload_session(site, channel)

    if session_info.get('status') == 'already_completed':
        return session_info['message']

    session_id = session_info['session_id']

    # Создаем папку на Яндекс.Диске
    name_channel = get_name_channel.get_name_channel(site, channel)
    name_folder = f"difm/{site}/{channel}_{name_channel}/"

    exists = check_name_folder.check_folder_exists(oauth_token, name_folder)
    if not exists:
        res = make_folder.make_y_folder(oauth_token, name_folder)
        if res:
            print(f"Папка '{name_folder}' создана на Яндекс.Диске")
        else:
            return "Ошибка создания папки на Яндекс.Диске"

    # Публикуем папку
    public_link = publish_folder.publish_and_get_public_link(oauth_token,
                                                             name_folder)
    if public_link:
        print(f"Публичная ссылка: {public_link}")
        res = set_publish_link_expiry.update_public_folder_settings(oauth_token,
                                                                    name_folder,
                                                                    days)
        if res:
            print(f"Ссылка будет действовать {days} дней.")
    else:
        print("Не удалось получить публичную ссылку.")

    data_link = get_random_acсess.get_access_data()

    # Получаем статус для отображения
    status = redis_set.get_session_status(session_id)
    print(f"Начало загрузки: {status['progress']} треков")

    # Загружаем треки по одному
    while True:
        track = redis_set.get_next_track(session_id)
        if not track:
            break

        result = upload_single_track(session_id, track, name_folder, data_link)
        print(f"Трек {track['track']}: {result['message']}")

        # Обновляем статус каждые 10 треков
        status = redis_set.get_session_status(session_id)
        if status['uploaded_tracks'] % 10 == 0:
            print(f"Прогресс: {status['progress']}")

        time.sleep(random.randint(10, 20))

    # Завершаем сессию
    redis_set.complete_session(session_id)
    final_status = redis_set.get_session_status(session_id)

    return f"Загрузка завершена. {final_status['uploaded_tracks']} из {final_status['total_tracks']} треков загружено успешно."