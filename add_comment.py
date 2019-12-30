import requests

request_url = "http://192.168.1.210:8000"

id = "fc42j0e"
sub = "mousemarket"

print(requests.post(request_url + "/add-comment/", {"sub_name": sub, "comment_id": id}))
