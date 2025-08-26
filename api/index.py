import requests
from flask import Flask, request, jsonify
import redis_set
import main
import uuid
import json
import threading
import time
from storage_manager import storage_manager

app = Flask(__name__)


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

    # Получаем информацию о канале и треках
    channel_info = main.get_channel_info(site, channel)

    if 'error' in channel_info:
        return jsonify(channel_info), 400

    # Создаем задачу в хранилище
    task_data = {
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
        'data_link': channel_info['data_link'],
        'errors': []
    }

    task_id = storage_manager.create_task(task_data)

    if not task_id:
        return jsonify({'error': 'Не удалось создать задачу'}), 500

    # Запускаем автоматическую загрузку в фоновом потоке
    def background_upload():
        storage_manager.update_task(task_id,
                                    {'status': 'processing', 'started': True})

        tracks = channel_info['tracks']
        data_link = channel_info['data_link']

        for i in range(len(tracks)):
            # Проверяем статус задачи
            current_task = storage_manager.get_task(task_id)
            if not current_task or current_task.get('status') == 'cancelled':
                break

            track = tracks[i]
            result = main.upload_single_track_with_retry(
                site,
                channel,
                track,
                channel_info['public_link'],
                data_link
            )

            # Обновляем прогресс
            storage_manager.update_task(task_id, {
                'current_track': i + 1,
                'last_updated': time.time()
            })

            # Сохраняем ошибки если есть
            if 'error' in result:
                error_info = {
                    'track': track['track'],
                    'error': result['error'],
                    'attempt': time.time()
                }
                current_errors = current_task.get('errors', [])
                current_errors.append(error_info)
                storage_manager.update_task(task_id, {'errors': current_errors})
                print(
                    f"Ошибка при загрузке трека {track['track']}: {result['error']}")
            else:
                print(
                    f"Успешно загружен трек {i + 1}/{len(tracks)}: {track['track']}")

            time.sleep(2)

        # Завершаем задачу
        current_task = storage_manager.get_task(task_id)
        if current_task and current_task.get('status') != 'cancelled':
            storage_manager.update_task(task_id, {'status': 'completed',
                                                  'completed_at': time.time()})
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
            'public_link': channel_info['public_link'],
            'data_link_obtained': channel_info['data_link'] is not None
        },
        'message': f'Начинаем автоматическую загрузку {channel_info["total_tracks"]} треков.'
    })


@app.route('/upload_next/<task_id>')
def upload_next(task_id):
    """Endpoint для ручной загрузки следующего трека"""
    task = storage_manager.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    if task.get('status') == 'completed':
        return jsonify({
            'status': 'completed',
            'message': 'Все треки уже загружены',
            'public_link': task.get('public_link')
        })

    if task.get('current_track', 0) >= task.get('total_tracks', 0):
        storage_manager.update_task(task_id, {'status': 'completed'})
        return jsonify({
            'status': 'completed',
            'message': 'Все треки загружены',
            'public_link': task.get('public_link')
        })

    # Загружаем следующий трек
    tracks = task.get('tracks', [])
    current_track_index = task.get('current_track', 0)

    if current_track_index >= len(tracks):
        return jsonify({'error': 'No more tracks to process'}), 400

    track = tracks[current_track_index]
    result = main.upload_single_track_with_retry(
        task.get('site'),
        task.get('channel'),
        track,
        task.get('public_link'),
        task.get('data_link')
    )

    # Обновляем прогресс
    new_current_track = current_track_index + 1
    storage_manager.update_task(task_id, {'current_track': new_current_track})

    # Сохраняем ошибки если есть
    if 'error' in result:
        errors = task.get('errors', [])
        errors.append({
            'track': track['track'],
            'error': result['error'],
            'attempt': time.time()
        })
        storage_manager.update_task(task_id, {'errors': errors})

    completed = new_current_track >= task.get('total_tracks', 0)
    if completed:
        storage_manager.update_task(task_id, {'status': 'completed'})

    return jsonify({
        'task_id': task_id,
        'status': 'completed' if completed else 'processing',
        'current_track': new_current_track,
        'total_tracks': task.get('total_tracks'),
        'track_name': track['track'],
        'result': result,
        'next_url': f'/upload_next/{task_id}' if not completed else None
    })


@app.route('/task_status/<task_id>')
def task_status(task_id):
    task = storage_manager.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    total_tracks = task.get('total_tracks', 0)
    current_track = task.get('current_track', 0)

    response = {
        'task_id': task_id,
        'status': task.get('status', 'unknown'),
        'current_track': current_track,
        'total_tracks': total_tracks,
        'progress_percentage': round((current_track / total_tracks) * 100,
                                     1) if total_tracks > 0 else 0,
        'public_link': task.get('public_link'),
        'site': task.get('site'),
        'channel': task.get('channel'),
        'name_channel': task.get('name_channel'),
        'total_size_gb': task.get('total_size_gb'),
        'estimated_time_hours': task.get('estimated_time_hours'),
        'data_link_obtained': task.get('data_link') is not None,
        'errors_count': len(task.get('errors', [])),
        'created_at': task.get('created_at'),
        'updated_at': task.get('updated_at')
    }

    return jsonify(response)


@app.route('/cancel_task/<task_id>')
def cancel_task(task_id):
    if storage_manager.update_task(task_id, {'status': 'cancelled'}):
        return jsonify({'status': 'cancelled', 'message': 'Задача отменена'})
    else:
        return jsonify({'error': 'Task not found'}), 404


@app.route('/list_tasks')
def list_tasks():
    tasks = storage_manager.get_all_tasks()
    return jsonify({
        'total_tasks': len(tasks),
        'tasks': {task_id: {
            'status': task_data.get('status'),
            'site': task_data.get('site'),
            'channel': task_data.get('channel'),
            'progress': f"{task_data.get('current_track', 0)}/{task_data.get('total_tracks', 0)}",
            'data_link_obtained': task_data.get('data_link') is not None,
            'created_at': task_data.get('created_at')
        } for task_id, task_data in tasks.items()}
    })


@app.route('/clean_tasks')
def clean_tasks():
    """Очищает все задачи (для отладки)"""
    tasks = storage_manager.get_all_tasks()
    for task_id in list(tasks.keys()):
        storage_manager.delete_task(task_id)
    return jsonify(
        {'message': 'All tasks cleaned', 'cleaned_count': len(tasks)})


if __name__ == '__main__':
    app.run(debug=True)