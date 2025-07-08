from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def handle_request():
    # Получаем параметры из запроса
    name = request.args.get('name', default='')
    chat_id = request.args.get('id', default='0')
    item = request.args.get('item', default='')

    # Формируем ответ
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
    return 'About...'
