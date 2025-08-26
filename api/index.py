import requests
from flask import Flask, request, jsonify
import redis_set
import main
import uuid
import json
import threading
import time

app = Flask(__name__)

# Временное хранилище для состояния задач
tasks = {}


@app.route('/')
def handle_request():
    name = request.args.get('name', default='')
    chat_id = request.args.get('id', default='0')

    response = {
        name: True,
        "chatId": int(chat_id),
        "data": {
            "login": True,
            "chat_id": int(chat_id)
        }
    }

    return jsonify(response)


@app.route('/upload')
def upload():
    site = request.args.get('site')
    channel = request.args.get('channel')

    # Создаем уникальный ID задачи
    task_id = str(uuid.uuid4())

    # Получаем информацию о канале и треках
    channel_info = main.get_channel_info(site, channel)

    if 'error' in channel_info:
        return jsonify(channel_info), 400

    # Инициализируем задачу
    tasks[task_id] = {
        'status': 'pending',
        'site': site,
        'channel': channel,
        'name_channel': channel_info['name_channel'],
        'current_track': 0,
        'total_tracks': channel_info['total_tracks'],
        'public_link': channel_info['public_link'],
        'tracks': channel_info['tracks'],
        'total_size_gb': channel_info['total_size_gb'],
        'estimated_time_hours': channel_info['estimated_time_hours'],
        'started': False
    }

    # Запускаем автоматическую загрузку в фоновом потоке
    def background_upload():
        tasks[task_id]['status'] = 'processing'
        tasks[task_id]['started'] = True

        for i in range(len(tasks[task_id]['tracks'])):
            if tasks[task_id]['status'] == 'cancelled':
                break

            track = tasks[task_id]['tracks'][i]
            result = main.upload_single_track(
                site,
                channel,
                track,
                tasks[task_id]['public_link']
            )

            tasks[task_id]['current_track'] = i + 1

            # Обновляем статус для каждого трека
            if 'error' in result:
                tasks[task_id]['last_error'] = result['error']
                print(
                    f"Ошибка при загрузке трека {track['track']}: {result['error']}")
            else:
                print(
                    f"Успешно загружен трек {i + 1}/{len(tasks[task_id]['tracks'])}: {track['track']}")

            # Небольшая пауза между загрузками
            time.sleep(2)

        if tasks[task_id]['status'] != 'cancelled':
            tasks[task_id]['status'] = 'completed'
            print(f"Задача {task_id} завершена")

    # Запускаем фоновый поток
    thread = threading.Thread(target=background_upload)
    thread.daemon = True
    thread.start()

    return jsonify({
        'task_id': task_id,
        'status': 'started',
        'channel_info': {
            'name_channel': channel_info['name_channel'],
            'total_tracks': channel_info['total_tracks'],
            'total_size_gb': channel_info['total_size_gb'],
            'estimated_time_hours': channel_info['estimated_time_hours'],
            'public_link': channel_info['public_link']
        },
        'message': f'Начинаем автоматическую загрузку {channel_info["total_tracks"]} треков.'
    })


@app.route('/upload_next/<task_id>')
def upload_next(task_id):
    """Endpoint для ручного управления (если нужно)"""
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404

    task = tasks[task_id]

    if task['status'] == 'completed':
        return jsonify({
            'status': 'completed',
            'message': 'Все треки уже загружены',
            'public_link': task['public_link']
        })

    if task['current_track'] >= task['total_tracks']:
        task['status'] = 'completed'
        return jsonify({
            'status': 'completed',
            'message': 'Все треки загружены',
            'public_link': task['public_link']
        })

    # Загружаем следующий трек
    track = task['tracks'][task['current_track']]
    result = main.upload_single_track(
        task['site'],
        task['channel'],
        track,
        task['public_link']
    )

    task['current_track'] += 1

    return jsonify({
        'task_id': task_id,
        'status': 'processing',
        'current_track': task['current_track'],
        'total_tracks': task['total_tracks'],
        'track_name': track['track'],
        'result': result,
        'next_url': f'/upload_next/{task_id}' if task['current_track'] < task[
            'total_tracks'] else None
    })


@app.route('/task_status/<task_id>')
def task_status(task_id):
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404

    task = tasks[task_id]

    response = {
        'task_id': task_id,
        'status': task['status'],
        'current_track': task['current_track'],
        'total_tracks': task['total_tracks'],
        'progress_percentage': round(
            (task['current_track'] / task['total_tracks']) * 100, 1) if task[
                                                                            'total_tracks'] > 0 else 0,
        'public_link': task['public_link'],
        'site': task['site'],
        'channel': task['channel'],
        'name_channel': task['name_channel'],
        'total_size_gb': task['total_size_gb'],
        'estimated_time_hours': task['estimated_time_hours']
    }

    if 'last_error' in task:
        response['last_error'] = task['last_error']

    return jsonify(response)


@app.route('/cancel_task/<task_id>')
def cancel_task(task_id):
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404

    tasks[task_id]['status'] = 'cancelled'
    return jsonify({'status': 'cancelled', 'message': 'Задача отменена'})


@app.route('/list_tasks')
def list_tasks():
    return jsonify({
        'total_tasks': len(tasks),
        'tasks': {task_id: {
            'status': task['status'],
            'site': task['site'],
            'channel': task['channel'],
            'progress': f"{task['current_track']}/{task['total_tracks']}"
        } for task_id, task in tasks.items()}
    })


if __name__ == '__main__':
    app.run(debug=True)