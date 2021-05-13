import sys
sys.path.insert(0, '.')
import config
from server import JsonHelper
from swap import update_single_user_flair, get_sister_sub_count
import argparse
import praw
import time
import datetime

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
keys = mods = [str(x).lower() for x in sub.moderator()]
for i in range(len(keys)):
	user = keys[i]
	try:
		print(str(i) + ") Updating user " + user + " to flair " + str(len(db[args.sub_name.lower()][user])))
	except:
		continue
	try:
		age = datetime.timedelta(seconds=(time.time() - reddit.redditor(user).created_utc)).days / 365.0
	except:
		print("Unable to get age for " + user)
		age = 0
	count_int = len(db[args.sub_name.lower()][user]) + get_sister_sub_count(user, sub_config.gets_flair_from)
	try:
		update_single_user_flair(sub, sub_config, user, str(count_int), unassigned_users, age)
	except:
		unassigned_users.append(user)

print("The following users did not get their flair updated:\n  " + "\n  ".join(unassigned_users))
