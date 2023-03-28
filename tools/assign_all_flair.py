import sys
sys.path.insert(0, '.')
from swap import update_single_user_flair, get_swap_count, create_reddit_and_sub, update_flair
import requests
import argparse
import praw
import time
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('sub_name', metavar='C', type=str)
args = parser.parse_args()

platform = 'reddit'

sub_config, reddit, sub = create_reddit_and_sub(args.sub_name.lower())

request_url = "http://0.0.0.0:8000"
db = requests.get(request_url+"/get-db/").json()

if sub_config.subreddit_name not in db:
	db[sub_config.subreddit_name] = {}
if platform not in db[sub_config.subreddit_name]:
	db[sub_config.subreddit_name][platform] = {}

unassigned_users = []
keys = db[sub_config.subreddit_name][platform].keys()
mods = [str(x).lower() for x in sub.moderator()]
keys = mods

keys = ['dimitritelep2113']

for i in range(len(keys)):
	user = keys[i].lower()
	if user not in db[sub_config.subreddit_name][platform]:
		db[sub_config.subreddit_name][platform][user] = []
#	count = str(get_swap_count(user, [sub_config.subreddit_name] + sub_config.gets_flair_from, platform))
	try:
		print(str(i) + ") Updating user " + user)
	except Exception as e:
		continue
	try:
		redditor = reddit.redditor(user)
		age = datetime.timedelta(seconds=(time.time() - redditor.created_utc)).days / 365.0
		update_flair(redditor, None, sub_config)
#		update_single_user_flair(sub, sub_config, str(redditor), count, unassigned_users, age)
		time.sleep(0.5)
	except:
		time.sleep(20)
		try:
			redditor = reddit.redditor(user)
			age = datetime.timedelta(seconds=(time.time() - redditor.created_utc)).days / 365.0
			update_flair(redditor, None, sub_config)
#			update_single_user_flair(sub, sub_config, str(redditor), count, unassigned_users, age)
			time.sleep(0.5)
		except Exception as e:
			print("    Unable to update flair for " + user + " with error " + str(e))
			unassigned_users.append(user)


if unassigned_users:
	print("The following users did not get their flair updated:\n  " + "\n  ".join(unassigned_users))

