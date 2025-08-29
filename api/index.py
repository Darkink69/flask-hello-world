from flask import Flask, request, jsonify
import redis_set
import main
import time

app = Flask(__name__)


@app.route('/')
def handle_request():
    name = request.args.get('name', default='')
    chat_id = request.args.get('id', default='0')
    item = request.args.get('item', default='')
    return ' /upload?site=jazzradio&channel=519'


@app.route('/red')
def red():
    res = redis_set.red()
    return jsonify(res)


@app.route('/upload')
def upload():
    site = request.args.get('site')
    channel = request.args.get('channel')
    res = main.upload_mp3(site, channel)
    return res


@app.route('/upload/status/<session_id>')
def upload_status(session_id):
    status = redis_set.get_session_status(session_id)
    return jsonify(status)


@app.route('/upload/start')
def start_upload():
    site = request.args.get('site')
    channel = request.args.get('channel')

    # Инициализируем сессию
    session_info = redis_set.initialize_upload_session(site, channel)

    if session_info.get('status') == 'already_completed':
        return jsonify({
            "status": "error",
            "message": "Этот набор треков уже был загружен ранее"
        })

    return jsonify({
        "status": "started",
        "session_id": session_info['session_id'],
        "message": "Сессия загрузки инициализирована. Используйте /upload/next для загрузки треков"
    })


@app.route('/upload/next/<session_id>')
def upload_next(session_id):
    track = redis_set.get_next_track(session_id)
    if not track:
        # Завершаем сессию если все треки обработаны
        redis_set.complete_session(session_id)
        status = redis_set.get_session_status(session_id)
        return jsonify({
            "status": "completed",
            "message": f"Все треки обработаны. Успешно: {status['uploaded_tracks']}, Ошибок: {status['failed_tracks']}"
        })

    # Здесь можно вызвать загрузку конкретного трека
    return jsonify({
        "status": "track_available",
        "track": track,
        "message": f"Следующий трек: {track['track']}"
    })


@app.route('/sessions/active')
def active_sessions():
    r = redis_set.get_redis_connection()
    sessions = r.smembers("active_sessions")

    result = []
    for session_id in sessions:
        status = redis_set.get_session_status(session_id)
        result.append({
            "session_id": session_id,
            "status": status
        })

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)