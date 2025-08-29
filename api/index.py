from flask import Flask, request, jsonify

import get_random_acсess
import redis_set
import main
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

    return 'Тут будет статус загрузки и тд. Загружается по по 5 штук в формате /upload?site=jazzradio&channel=519'

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

@app.route('/upload_one')
def upload_one_track():
    oauth_token = "y0__xC70devARjblgMg3NzV4xMIZ_XCL_u7KWPy_1nYK9cpmiVNUQ"
    # site = request.args.get('site')
    data_link = get_random_acсess.get_access_data()
    name_folder = f"difm/di/9_Hardcore/"
    track = '//content.audioaddict.com/prd/f/7/b/5/5/33647c1222f98799e6553199931849850c1.mp4'
    track_n = 'Uuurrraaaaa ura'
    file_url = 'https:' + track + '?' + data_link
    filename = track_n + '.mp3'
    res = upload_url_file.upload_file_to_yandex_disk_from_url(oauth_token,
                                                              name_folder,
                                                              filename,
                                                              file_url)
    return res

if __name__ == '__main__':
    app.run(debug=True)