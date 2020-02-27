import requests

request_url = "http://192.168.0.248:8000"

sub = "digitalcodesell"
ids = ["fc5x9pe", "fc5pmpy", "fa8d7ys"]

for id in ids:
	print(requests.post(request_url + "/add-comment/", {"sub_name": sub, "comment_id": id}))
