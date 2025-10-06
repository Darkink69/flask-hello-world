from flask import Flask, request, jsonify
import redis_set
import main
import get_order_channels

app = Flask(__name__)

@app.route('/')
def handle_request():
    name = request.args.get('name', default='')
    chat_id = request.args.get('id', default='0')
    item = request.args.get('item', default='')
    return ' /upload?site=jazzradio&channel='

@app.route('/order')
def get_order():
    name = request.args.get('name', default='')
    res = get_order_channels.process_channels(name)
    return res

@app.route('/red')
def red():
    # id = request.args.get()
    res = redis_set.red()
    return jsonify(res)

@app.route('/upload')
def upload():
    site = request.args.get('site')
    channel = request.args.get('channel')
    order = request.args.get('order')
    res = main.upload_mp3(site, channel, order)
    return (res

@app.route('/upload_one'))
def upload_one():
    site = request.args.get('site')
    channel = request.args.get('channel')
    id_track = request.args.get('id_track')
    # order = request.args.get('order')
    res = main.upload_one_mp3(site, channel, id_track)
    return res


if __name__ == '__main__':
    app.run(debug=True)