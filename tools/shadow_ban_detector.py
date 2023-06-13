import praw
import sys
sys.path.insert(0, '.')
import Config
import os

sub_config = Config.Config('funkoppopmod')
reddit = sub_config.reddit_object

subnames = [x.split("-")[0] for x in os.listdir("config/")]
for subname in subnames:
	sub_config = Config.Config(subname.split(".")[0])
	if not sub_config.bot_username:
		continue
	try:
		bot = reddit.redditor(sub_config.bot_username)
		m = bot.is_mod
	except Exception as e:
		print("[" + subname + "] " + sub_config.bot_username + " is shadowbanned.")
