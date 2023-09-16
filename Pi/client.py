import requests

URL = "http://172.29.103.161:5000/send_image"

files = {'image': open('./YERB.png', 'rb')}
r = requests.post(URL, files=files)

print(r)