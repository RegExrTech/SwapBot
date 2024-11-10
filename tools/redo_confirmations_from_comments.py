import time
import praw
import os
import sys
sys.path.insert(0, '.')
import Config
import server
import requests

j = server.JsonHelper()

db = j.get_db('database/comments.json')
request_url = "http://0.0.0.0:8000"

timestamp = 1720902600

subnames = [x.split(".")[0] for x in os.listdir("config/")]
for subname in subnames:
	subname = subname.split(".")[0]
	if subname != 'digitalcodesell':
		continue
	print("=== " + subname + " ===")
	sub_config = Config.Config(subname)
	if not sub_config.bot_username or sub_config.disabled:
		print("skipping...")
		continue
	bot_obj = sub_config.reddit_object.redditor(sub_config.bot_username)
	comments = bot_obj.comments.new(limit=None)
	for comment in comments:
		if comment.created_utc < timestamp:
			print("Done, confirmation was made at " + str(comment.created_utc))
			break
#		if comment.created_utc > time.time() - (10*60):
#			print("Found a comment made recently. Skipping...")
#			continue
		if not '->' in comment.body:
			continue
		lines = [x for x in comment.body.splitlines() if '* ' in x]
		users = [x.split('u/')[1].split(' ')[0] for x in lines]
		top_comment = comment.parent().parent()
		if top_comment.id not in db[sub_config.subreddit_name]["reddit"]["active"] and top_comment.id not in db[sub_config.subreddit_name]["reddit"]["archived"]:
#			print("https://www.reddit.com/r/" + sub_config.subreddit_name + "/comments/" + parent_post.id + "/-/" + top_comment.id)
			print(users)
			print(top_comment.id)
			requests.post(request_url + "/add-comment/", {'sub_name': sub_config.subreddit_name, 'platform': 'reddit', 'comment_id': top_comment.id})
