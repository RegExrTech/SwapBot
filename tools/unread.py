import praw
import sys
sys.path.insert(0, '.')
import Config
import os

subnames = [x.split("-")[0] for x in os.listdir("config/")]
for subname in subnames:
	print("=== " + subname + " ===")
	sub_config = Config.Config(subname.split(".")[0])
	if not sub_config.bot_username:
		print("skipping...")
		continue
	reddit = sub_config.reddit_object
	for message in reddit.inbox.all(limit=None):
		if message.created_utc < 1704247245:
			break
		message.mark_unread()
		print("marking unread...")
