#TODO only go back to the last hour, rather than an arbitrary number of comments (i.e.50)
import praw
import argparse
sys.path.insert(0, '.')
import Config
import os

#parser = argparse.ArgumentParser()
#parser.add_argument('config_file_name', metavar='C', type=str)
#args = parser.parse_args()
#config_fname = 'config/' + args.config_file_name
subnames = [x.split("-")[0] for x in os.listdir("config/")]
for subname in subnames:
	sub_config = Config.Config(subname.split(".")[0])
	reddit = sub_config.reddit_object
	for message in reddit.inbox.all(limit=50):
		message.mark_unread()
