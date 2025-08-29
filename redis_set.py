import redis
from flask import jsonify

import get_json_channel


def red(id):
    r = redis.Redis.from_url("redis://default:JRxLZs5NT8kSGmqTGftkAAPRMvz2FRrq@redis-16294.c281.us-east-1-2.ec2.redns.redis-cloud.com:16294")

    # Проверка подключения
    try:
        r.ping()
        print("Успешное подключение к Redis!")

    except redis.ConnectionError:
        print("Ошибка подключения к Redis")

    url_ch = 'https://qh8bsvaksadb2kj9.public.blob.vercel-storage.com/di/db_di_full_69_light.json'
    tracks = get_json_channel.get_json_channel_tracks(url_ch)

    r.set("track", tracks[0]["track"])
    r.set( "url", tracks[0]["url"])
    one = r.get("track")
    two = r.get("url")
    print(one, two)

    return one, two

    # # Запись значения
    # r.set("user:1", "Alice")
    #
    # # Чтение значения
    # name = r.get("user:1")  # b'Alice' (возвращает bytes)
    # print(name.decode())    # 'Alice' (преобразуем в строку)
    #
    # # Удаление ключа
    # # r.delete("user:1")
    #
    #
    # # Добавление в список
    # r.lpush("messages", "Hello")
    # r.lpush("messages", "World")
    #
    # # Получение элементов
    # messages = r.lrange("messages", 0, -1)  # [b'World', b'Hello']
    # print([msg.decode() for msg in messages])
    #
    #
    #
    # # Запись в хэш
    # r.hset(id, mapping={"name": "Bob", "age": "30"})
    #
    # # Чтение поля
    # print(r.hget(id, "name"))  # b'Bob'
    #
    # # Чтение всего хэша
    # print(r.hgetall(id))  # {b'name': b'Bob', b'age': b'30'}
    #
    #
    #
    #
    # # Добавление элементов
    # r.sadd("fruits", "apple", "banana", "orange")
    #
    # # Проверка наличия элемента
    # print(r.sismember("fruits", "apple"))  # True
    #
    # # Получение всех элементов
    # print(r.smembers("fruits"))  # {b'banana', b'orange', b'apple'}
    # return 'usa red 2'