from flask import Flask, request, jsonify
import redis_set
import main

app = Flask(__name__)

@app.route('/')
def handle_request():
    name = request.args.get('name', default='')
    chat_id = request.args.get('id', default='0')
    item = request.args.get('item', default='')

    return ' /upload?site=jazzradio&channel=519'

@app.route('/red')
def red():
    # id = request.args.get()
    res = redis_set.red()
    return jsonify(res)

@app.route('/upload')
def upload():
    site = request.args.get('site')
    channel = request.args.get('channel')
    res = main.upload_mp3(site, channel)
    return res


if __name__ == '__main__':
    app.run(debug=True)