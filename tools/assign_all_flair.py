import sys
sys.path.insert(0, '.')
from server import JsonHelper
from swap import update_single_user_flair, get_swap_count, create_reddit_and_sub, update_flair
import argparse
import praw
import time
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('sub_name', metavar='C', type=str)
args = parser.parse_args()

platform = 'reddit'

sub_config, reddit, sub = create_reddit_and_sub(args.sub_name.lower())

json_helper = JsonHelper()
db = json_helper.get_db('database/swaps.json')

if sub_config.subreddit_name not in db:
	db[sub_config.subreddit_name] = {}
if platform not in db[sub_config.subreddit_name]:
	db[sub_config.subreddit_name][platform] = {}

unassigned_users = []
keys = db[sub_config.subreddit_name][platform].keys()
mods = [str(x).lower() for x in sub.moderator()]

for i in range(len(keys)):
	user = keys[i].lower()
	if user not in db[sub_config.subreddit_name][platform]:
		db[sub_config.subreddit_name][platform][user] = []
	count = str(get_swap_count(user, [sub_config.subreddit_name] + sub_config.gets_flair_from, platform))
	try:
		print(str(i) + ") Updating user " + user + " to flair " + count)
	except Exception as e:
		continue
	try:
		redditor = reddit.redditor(user)
#		update_flair(redditor, None, sub_config)
		age = datetime.timedelta(seconds=(time.time() - redditor.created_utc)).days / 365.0
		update_single_user_flair(sub, sub_config, redditor, count, unassigned_users, age)
		time.sleep(0.5)
	except:
		time.sleep(20)
		try:
			redditor = reddit.redditor(user)
#			update_flair(redditor, None, sub_config)
			age = datetime.timedelta(seconds=(time.time() - redditor.created_utc)).days / 365.0
			update_single_user_flair(sub, sub_config, redditor, count, unassigned_users, age)
			time.sleep(0.5)
		except:
			print("    Unable to update flair for " + user)
			unassigned_users.append(user)


if unassigned_users:
	print("The following users did not get their flair updated:\n  " + "\n  ".join(unassigned_users))
