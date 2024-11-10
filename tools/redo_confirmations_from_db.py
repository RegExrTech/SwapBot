import time
import praw
import os
import sys
sys.path.insert(0, '.')
import Config
import server
import requests

j = server.JsonHelper()

request_url = "http://0.0.0.0:8000"

timestamp = 1722439800

subnames = [x.split(".")[0] for x in os.listdir("config/")]
for subname in subnames:
	print("=== " + subname + " ===")
	sub_config = Config.Config(subname.split(".")[0])
	if not sub_config.bot_username or sub_config.disabled:
		print("skipping...")
		continue
	db = requests.get(request_url+"/get-sub-db/", data={'sub': sub_config.subreddit_name}).json()
	for user in db['reddit'].keys():
		for transaction in db['reddit'][user]['transactions']:
			if transaction['timestamp'] > timestamp:
				print(transaction)
				requests.post(request_url + "/add-comment/", {'sub_name': sub_config.subreddit_name, 'platform': 'reddit', 'comment_id': transaction['comment_id']})
