import redis

# r = redis.Redis(
#     host='redis-14960.c81.us-east-1-2.ec2.redns.redis-cloud.com',
#     port=14960,
#     decode_responses=True,
#     username="default",
#     password="XbgQFnKXv4iW3w2ExSH5fTX3nId929tP",
# )

def red():
    r = redis.Redis.from_url("redis://default:5vZ4S25Eq1moXDQT1yyulhGlayl9fNZk@redis-12865.c340.ap-northeast-2-1.ec2.redns.redis-cloud.com:12865")

    # success = r.set("foo", "bar")
    # # True
    #
    # result = r.get("foo")
    # print(result)
    # >>> bar


    # Проверка подключения
    try:
        r.ping()
        print("Успешное подключение к Redis!")
    except redis.ConnectionError:
        print("Ошибка подключения к Redis")


    # Запись значения
    r.set("user:1", "Alice")

    # Чтение значения
    name = r.get("user:1")  # b'Alice' (возвращает bytes)
    print(name.decode())    # 'Alice' (преобразуем в строку)

    # Удаление ключа
    # r.delete("user:1")


    # Добавление в список
    r.lpush("messages", "Hello")
    r.lpush("messages", "World")

    # Получение элементов
    messages = r.lrange("messages", 0, -1)  # [b'World', b'Hello']
    print([msg.decode() for msg in messages])
    #
    #
    #
    # # Запись в хэш
    # r.hset("user:1000", mapping={"name": "Bob", "age": "30"})
    #
    # # Чтение поля
    # print(r.hget("user:1000", "name"))  # b'Bob'
    #
    # # Чтение всего хэша
    # print(r.hgetall("user:1000"))  # {b'name': b'Bob', b'age': b'30'}
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
    return 'ok'