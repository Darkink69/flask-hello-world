import get_name_channel

oauth_token = "y0__xC70devARjblgMg3NzV4xMIZ_XCL_u7KWPy_1nYK9cpmiVNUQ"  # Ваш OAuth-токен

# загрузка по одному, должна быть на сервере
def upload_one_mp3(site=0, channel='none', id_track=0):
    url_ch = f'https://qh8bsvaksadb2kj9.public.blob.vercel-storage.com/{site}/db_{site}_full_{channel}_premium_light.json'

    name_channel = get_name_channel.get_name_channel(site, channel)
    print(name_channel)
    print(site, channel, id_track, '!!!')
    return f'работает {channel}, {site}, {id_track}, {name_channel} качается!'
