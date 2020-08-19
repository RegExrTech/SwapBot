import sys
sys.path.insert(0, '.')
import config
from server import JsonHelper
from swap import update_single_user_flair
import requests
import argparse
import praw

parser = argparse.ArgumentParser()
parser.add_argument('sub_name', metavar='C', type=str)
args = parser.parse_args()

sub_config = config.Config(args.sub_name.lower())

reddit = praw.Reddit(client_id=sub_config.client_id, client_secret=sub_config.client_secret, user_agent='UserAgent', username=sub_config.bot_username, password=sub_config.bot_password)
sub = reddit.subreddit(sub_config.subreddit_name)

json_helper = JsonHelper()
db = json_helper.get_db('database/swaps.json')

unassigned_users = []
keys = db[args.sub_name.lower()].keys()
for i in range(len(keys)):
	user = keys[i]
	print(str(i) + ") Updating user " + user + " to flair " + str(len(db[args.sub_name.lower()][user])))
	try:
		update_single_user_flair(sub, sub_config, user, str(len(db[args.sub_name.lower()][user])), unassigned_users)
	except:
		unassigned_users.append(user)

print("The following users did not get their flair updated:\n  " + "\n  ".join(unassigned_users))
