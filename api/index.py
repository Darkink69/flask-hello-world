from flask import Flask, request, jsonify
import redis_set
import upload_url_file

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

@app.route('/red')
def red():
    id = request.args.get('id', default='no_name')
    res = redis_set.red(id)
    return res@app.route('/red')

@app.route('/upload')
def upload():
    filename = request.args.get('filename', default='no_name')
    res = upload_url_file.upload_file_to_yandex_disk_from_url(filename)
    return res

if __name__ == '__main__':
    app.run(debug=True)