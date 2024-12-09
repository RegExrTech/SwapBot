import time
import threading
import sys
import os
import datetime
sys.path.insert(0, '.')
import Config
import server

SUB_NAME = 'watchexchange'
UPDATE_TIME = 1727157780

content_dict = {}
c = Config.Config(SUB_NAME)

def get_configs():
	to_return = []
	ignores = ["WatchExBot"]
	subnames = [x.split(".")[0] for x in os.listdir("config/")]
	for subname in subnames:
		config = Config.Config(subname)
		if config.bot_username in ignores:
			continue
		to_return.append(config)
	return to_return

def get_mod_actions(sub_config, last_update_time, before=None):
	actions = []
	try:
		if before is not None:
			action_generator = sub_config.subreddit_object.mod.log(limit=None, params={'after':before.id})
		else:
			action_generator = sub_config.subreddit_object.mod.log(limit=None)
	except Exception as e:
		print(sub_config.subreddit_name + " was unable to get mod actions when checking for bans with error " + str(e))
		return actions
	found_last_action = False
	try:
		for action in action_generator:
			if action.created_utc <= last_update_time:
				found_last_action = True
				break
			actions.append(action)
	except Exception as e:
		print("    r/" + sub_config.subreddit_name + " was unable to continue scraping the mod log with error " + str(e) + ". Skipping iteration and trying again.")
		return []
	if len(actions) == 0:
		found_last_action = True
	if not found_last_action:
		return actions + get_mod_actions(sub_config, last_update_time, before=actions[-1])
	return actions

actions = get_mod_actions(c, UPDATE_TIME)

users = set()
for action in actions:
	if action.action == 'wikirevise' and 'confirmations/' in action.details:
		users.add(action.details.split("/")[1].split(" ")[0])

users = list(users)
users.sort()
print("Starting to iterate through " + str(len(users)) + " users...")

def get_db():
	swap_data = {}
	for fname in os.listdir('database'):
		if '-swaps.json' in fname and SUB_NAME + '-' in fname:
			try:
				_db = server.json_helper.get_db('database/'+fname)
			except Exception as e:
				print("Unable to load database for " + fname + " with error " + str(e))
				raise e
			_sub_name = fname.split("-")[0]
			if _sub_name in swap_data:
				for platform in _db:
					if platform not in swap_data[_sub_name]:
						swap_data[_sub_name][platform] = _db[platform]
					else:
						swap_data[_sub_name][platform].update(_db[platform])
			else:
				swap_data[_sub_name] = _db
	return swap_data

db = get_db()[SUB_NAME]

mutex = threading.Lock()

def get_wiki_content(users, c):
	global content_dict
	for user in users:
		try:
			content = [x for x in c.subreddit_object.wiki['confirmations/' + user].content_md.splitlines() if x]
		except:
			print("Unable to get content for user " + user)
			content = []
		mutex.acquire()
		content_dict[user] = content
		mutex.release()
		time.sleep(1)

configs = get_configs()
slice_count = len(users)//len(configs)
threads = []
for count, bot_config in enumerate(configs):
	bot_config.subreddit_object = bot_config.reddit_object.subreddit(SUB_NAME)
	if count == len(configs)-1:
		user_slice = users[slice_count*count:]
	else:
		user_slice = users[slice_count*count:slice_count*(count+1)]
	t = threading.Thread(target=get_wiki_content, args=(user_slice, bot_config))
	threads.append(t)
	t.start()
for t in threads:
	t.join()
print("Done getting wiki content")

for user in users:
	if user not in db['reddit']:
		db['reddit'][user] = {"transactions": []}
	content = content_dict[user]
	print(user)
	for line in content:
		if 'Legacy Trades' in line:
			legacy_count = int(line.split(" ")[1])
			if 'legacy_count' not in db['reddit'][user] or db['reddit'][user]['legacy_count'] != legacy_count:
				db['reddit'][user]['legacy_count'] = legacy_count
		elif line.startswith("*  ["):
			if 'www.reddit.com/' in line:
				ids = line.split("comments/")[1].split(")")[0]
				post_id = ids.split("/")[0]
				comment_id = ids.split("/")[-1]
			else:
				post_id = line.split("redd.it/")[1].split(")")[0]
				comment_id = ""
			if '2024-' in line:
				ts_string = "2024" + line.split(" - 2024")[1].split(" - ")[0]
				timestamp = datetime.datetime.strptime(ts_string, "%Y-%m-%d").timestamp()
			else:
				timestamp = 0
			partner = line.split(" - u/")[1].split(" ")[0]
			if any([post_id == tr['post_id'] and comment_id == tr["comment_id"] and partner == tr['partner'] for tr in db['reddit'][user]['transactions']]):
				continue
			db['reddit'][user]['transactions'].append({"post_id": post_id, "comment_id": comment_id, "timestamp": timestamp, "partner": partner})
			print(db['reddit'][user]['transactions'][-1])

server.json_helper.dump(db, server.swaps_fname.format(sub_name=SUB_NAME), should_shard=True)
