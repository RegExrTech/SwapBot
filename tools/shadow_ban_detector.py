import praw
import sys
sys.path.insert(0, '.')
import Config
import os
sys.path.insert(0, 'logger')
import logger

database_fname = 'database/shadowbanned_bots.txt'
f = open(database_fname, 'r')
previously_banned = f.read().splitlines()
f.close()

sub_config = Config.Config('funkoppopmod')
reddit = sub_config.reddit_object

banned = []
subnames = [x.split("-")[0] for x in os.listdir("config/")]
for subname in subnames:
	sub_config = Config.Config(subname.split(".")[0])
	if not sub_config.bot_username:
		continue
	try:
		bot = reddit.redditor(sub_config.bot_username)
		m = bot.is_mod
	except Exception as e:
		banned.append(sub_config.bot_username)

newly_banned = [x for x in banned if x not in previously_banned]
no_longer_banned = [x for x in previously_banned if x not in banned]
if newly_banned:
	logger.log("The following swap bots are shadowbanned:\n\n* " + "\n* ".join(newly_banned))
if no_longer_banned:
	logger.log("The following swap bots are no longer shadowbanned:\n\n* " + "\n* ".join(no_longer_banned))

if newly_banned or no_longer_banned:
	f = open(database_fname, 'w')
	f.write("\n".join(banned))
	f.close()
