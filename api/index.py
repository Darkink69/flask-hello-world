from flask import Flask, request, jsonify
import redis

app = Flask(__name__)

@app.route('/')
def handle_request():
    name = request.args.get('name', default='')
    chat_id = request.args.get('id', default='0')
    item = request.args.get('item', default='')

    response = {
        name: True,
        "chatId": int(chat_id),
        "data": {
            "login": True,
            "chat_id" : int(chat_id)
        }
    }

    return jsonify(response)

@app.route('/about')
def about():
    r = redis.Redis.from_url(
        "redis://default:5vZ4S25Eq1moXDQT1yyulhGlayl9fNZk@redis-12865.c340.ap-northeast-2-1.ec2.redns.redis-cloud.com:12865")


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

    return result

if __name__ == '__main__':
    app.run(debug=True)