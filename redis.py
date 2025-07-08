import redis

# r = redis.Redis(
#     host='redis-14960.c81.us-east-1-2.ec2.redns.redis-cloud.com',
#     port=14960,
#     decode_responses=True,
#     username="default",
#     password="XbgQFnKXv4iW3w2ExSH5fTX3nId929tP",
# )

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

success = r.set('foo', 'bar')
# True

result = r.get('foo')
print(result)
# >>> bar

