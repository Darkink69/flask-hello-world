import time

import redis
import json
import hashlib
import get_json_channel


def get_redis_connection():
    return redis.Redis.from_url(
        "redis://default:JRxLZs5NT8kSGmqTGftkAAPRMv2FRrq@redis-16294.c281.us-east-1-2.ec2.redns.redis-cloud.com:16294")


def get_tracks_hash(tracks):
    """Создает хэш для идентификации набора треков"""
    tracks_str = json.dumps(tracks, sort_keys=True)
    return hashlib.md5(tracks_str.encode()).hexdigest()


def initialize_upload_session(site, channel):
    r = redis.Redis.from_url("redis://default:JRxLZs5NT8kSGmqTGftkAAPRMv2FRrq@redis-16294.c281.us-east-1-2.ec2.redns.redis-cloud.com:16294")

    try:
        r.ping()
        print("Успешное подключение к Redis!")
    except redis.ConnectionError:
        print("Ошибка подключения к Redis")
        return None

    url_ch = f'https://qh8bsvaksadb2kj9.public.blob.vercel-storage.com/{site}/db_{site}_full_{channel}_light.json'
    tracks = get_json_channel.get_json_channel_tracks(url_ch)

    # Создаем уникальный идентификатор сессии
    session_id = f"upload_session_{site}_{channel}"
    tracks_hash = get_tracks_hash(tracks)

    # Проверяем, не загружался ли уже этот набор треков
    completed_sessions = r.hgetall("completed_sessions")
    if tracks_hash in completed_sessions:
        return {"status": "already_completed",
                "message": "Этот набор треков уже был загружен ранее"}

    # Преобразуем треки и добавляем статус загрузки
    transformed_tracks = []
    for i, track in enumerate(tracks):
        transformed_track = {
            "id": track['id'],
            "track": track['track'],
            "url": track['url'],
            "uploaded": False,
            "attempts": 0,
            "last_attempt": None,
            "error": None,
            "index": i
        }
        transformed_tracks.append(transformed_track)

    # Сохраняем данные сессии
    session_data = {
        "site": site,
        "channel": channel,
        "total_tracks": len(transformed_tracks),
        "uploaded_tracks": 0,
        "failed_tracks": 0,
        "tracks_hash": tracks_hash,
        "start_time": json.dumps(int(time.time())),
        "status": "in_progress"
    }

    # Сохраняем в Redis одним pipeline для минимизации запросов
    with r.pipeline() as pipe:
        pipe.hset(session_id, mapping=session_data)
        pipe.set(f"{session_id}:tracks", json.dumps(transformed_tracks))
        pipe.sadd("active_sessions", session_id)
        pipe.execute()

    return {
        "session_id": session_id,
        "total_tracks": len(transformed_tracks),
        "status": "initialized"
    }


def get_next_track(session_id):
    r = get_redis_connection()

    tracks_data = r.get(f"{session_id}:tracks")
    if not tracks_data:
        return None

    tracks = json.loads(tracks_data)

    # Ищем первый не загруженный трек
    for track in tracks:
        if not track['uploaded'] and track[
            'attempts'] < 3:  # Максимум 3 попытки
            return track

    return None


def update_track_status(session_id, track_id, success=True, error_message=None):
    r = get_redis_connection()

    tracks_data = r.get(f"{session_id}:tracks")
    if not tracks_data:
        return False

    tracks = json.loads(tracks_data)

    for track in tracks:
        if track['id'] == track_id:
            track['uploaded'] = success
            track['attempts'] += 1
            track['last_attempt'] = json.dumps(int(time.time()))
            track['error'] = error_message
            break

    # Обновляем счетчики в сессии
    session_data = r.hgetall(session_id)
    if session_data:
        uploaded = int(session_data.get('uploaded_tracks', 0))
        failed = int(session_data.get('failed_tracks', 0))

        if success:
            uploaded += 1
        else:
            failed += 1

        with r.pipeline() as pipe:
            pipe.set(f"{session_id}:tracks", json.dumps(tracks))
            pipe.hset(session_id, "uploaded_tracks", uploaded)
            pipe.hset(session_id, "failed_tracks", failed)
            pipe.execute()

        return True

    return False


def complete_session(session_id):
    r = get_redis_connection()

    session_data = r.hgetall(session_id)
    if not session_data:
        return False

    tracks_hash = session_data.get('tracks_hash')

    with r.pipeline() as pipe:
        # Помечаем сессию как завершенную
        pipe.hset(session_id, "status", "completed")
        pipe.hset(session_id, "end_time", json.dumps(int(time.time())))

        # Добавляем в историю завершенных сессий
        if tracks_hash:
            pipe.hset("completed_sessions", tracks_hash, session_id)

        # Удаляем треки из Redis для экономии места
        pipe.delete(f"{session_id}:tracks")

        # Удаляем из активных сессий
        pipe.srem("active_sessions", session_id)

        pipe.execute()

    return True


def get_session_status(session_id):
    r = get_redis_connection()

    session_data = r.hgetall(session_id)
    if not session_data:
        return None

    return {
        "site": session_data.get('site'),
        "channel": session_data.get('channel'),
        "total_tracks": int(session_data.get('total_tracks', 0)),
        "uploaded_tracks": int(session_data.get('uploaded_tracks', 0)),
        "failed_tracks": int(session_data.get('failed_tracks', 0)),
        "status": session_data.get('status'),
        "progress": f"{int(session_data.get('uploaded_tracks', 0))}/{int(session_data.get('total_tracks', 0))}"
    }


def red():
    """Старая функция для обратной совместимости"""
    r = get_redis_connection()
    return {"message": "Используйте новые endpoints для управления загрузкой"}