import redis
import os
from flask import jsonify
import time


def test_redis_connection():
    """Тестирует подключение к Redis и возвращает результат"""
    results = {
        'success': False,
        'message': '',
        'connection_details': {},
        'error': None
    }

    try:
        # Получаем параметры подключения из переменных окружения
        redis_url = os.environ.get('REDIS_URL')
        redis_password = os.environ.get('REDIS_PASSWORD')
        redis_host = os.environ.get('REDIS_HOST')
        redis_port = os.environ.get('REDIS_PORT', '6379')
        redis_username = os.environ.get('REDIS_USERNAME')

        results['connection_details'] = {
            'REDIS_URL': redis_url,
            'REDIS_HOST': redis_host,
            'REDIS_PORT': redis_port,
            'REDIS_USERNAME': redis_username,
            'REDIS_PASSWORD_set': bool(redis_password)
        }

        print("Параметры подключения Redis:")
        for key, value in results['connection_details'].items():
            print(f"  {key}: {value}")

        # Пробуем разные варианты подключения
        client = None

        if redis_url:
            print("Попытка подключения через REDIS_URL...")
            client = redis.from_url(redis_url, decode_responses=True,
                                    socket_timeout=5, socket_connect_timeout=5)
        elif redis_host:
            print("Попытка подключения через отдельные параметры...")
            client = redis.Redis(
                host=redis_host,
                port=int(redis_port),
                password=redis_password,
                username=redis_username,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
        else:
            results['message'] = 'Не найдены параметры подключения к Redis'
            return results

        # Тестируем подключение
        print("Тестируем подключение...")
        start_time = time.time()

        # Простая команда PING
        response = client.ping()
        connection_time = time.time() - start_time

        if response:
            results['success'] = True
            results[
                'message'] = f'Успешное подключение к Redis! Время отклика: {connection_time:.3f} сек'
            results['connection_time'] = connection_time

            # Получаем дополнительную информацию
            try:
                info = client.info()
                results['redis_info'] = {
                    'version': info.get('redis_version'),
                    'mode': info.get('redis_mode'),
                    'used_memory': info.get('used_memory_human'),
                    'connected_clients': info.get('connected_clients')
                }
            except Exception as info_error:
                results['redis_info'] = {'error': str(info_error)}

        else:
            results[
                'message'] = 'Не удалось подключиться к Redis (PING не ответил)'

        client.close()

    except redis.ConnectionError as e:
        results['error'] = f'Ошибка подключения: {str(e)}'
        results['message'] = 'Не удалось установить соединение с Redis'

    except redis.AuthenticationError as e:
        results['error'] = f'Ошибка аутентификации: {str(e)}'
        results['message'] = 'Ошибка аутентификации в Redis'

    except redis.TimeoutError as e:
        results['error'] = f'Таймаут подключения: {str(e)}'
        results['message'] = 'Таймаут при подключении к Redis'

    except Exception as e:
        results['error'] = f'Неожиданная ошибка: {str(e)}'
        results['message'] = f'Произошла непредвиденная ошибка: {str(e)}'

    return results


def test_redis_operations():
    """Тестирует основные операции с Redis"""
    results = {
        'set_test': False,
        'get_test': False,
        'delete_test': False,
        'details': {}
    }

    try:
        connection_test = test_redis_connection()
        if not connection_test['success']:
            results['details'] = connection_test
            return results

        # Если подключение успешно, тестируем операции
        redis_url = os.environ.get('REDIS_URL')
        redis_password = os.environ.get('REDIS_PASSWORD')
        redis_host = os.environ.get('REDIS_HOST')
        redis_port = os.environ.get('REDIS_PORT', '6379')

        if redis_url:
            client = redis.from_url(redis_url, decode_responses=True)
        else:
            client = redis.Redis(
                host=redis_host,
                port=int(redis_port),
                password=redis_password,
                decode_responses=True
            )

        # Тест SET
        test_key = 'test:flask:connection'
        test_value = 'Hello from Flask! ' + str(time.time())

        set_result = client.set(test_key, test_value, ex=60)  # TTL 60 секунд
        results['set_test'] = bool(set_result)
        results['details']['set_result'] = set_result

        # Тест GET
        get_result = client.get(test_key)
        results['get_test'] = get_result == test_value
        results['details']['get_result'] = get_result
        results['details']['expected_value'] = test_value

        # Тест DELETE
        delete_result = client.delete(test_key)
        results['delete_test'] = delete_result == 1
        results['details']['delete_result'] = delete_result

        # Проверяем что ключ удален
        check_deleted = client.get(test_key)
        results['details']['after_delete_check'] = check_deleted is None

        client.close()

    except Exception as e:
        results['details']['error'] = str(e)

    return results