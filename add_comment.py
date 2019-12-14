import requests

request_url = "http://192.168.1.210:8000"

id = ""
sub = ""

requests.post(request_url + "/add-swap/", {'sub_name': sub, 'comment_id': id})
