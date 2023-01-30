import praw
import sys
sys.path.insert(0, '.')
import Config
import os

sub_config = Config.Config('funkoppopmod')

reddit = praw.Reddit(client_id=sub_config.client_id, client_secret=sub_config.client_secret, user_agent='Swap Bot for ' + sub_config.subreddit_name + ' v1.0 (by u/RegExr)', username=sub_config.bot_username, password=sub_config.bot_password)

subnames = [x.split("-")[0] for x in os.listdir("config/")]
for subname in subnames:
	sub_config = Config.Config(subname.split(".")[0])
	try:
		bot = reddit.redditor(sub_config.bot_username)
		m = bot.is_mod
	except Exception as e:
		print(sub_config.bot_username + " is shadowbanned.")
