import requests

site = 'di'
channel = 3
id_track = 333


url = f"https://flask-hello-world-delta-eosin.vercel.app/upload_one?site={site}&channel={channel}&id_track={id_track}"
headers = {
	"Content-Type": "application/json"
}


response = requests.get(url, headers=headers)
print(response.text)