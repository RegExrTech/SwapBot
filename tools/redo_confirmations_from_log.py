import time
import praw
import os
import sys
sys.path.insert(0, '.')
import Config
import server
import requests

j = server.JsonHelper()

db = j.get_db('database/comments.json')
request_url = "http://0.0.0.0:8000"

timestamp = 1717920120

def get_mod_actions(sub_config, last_update_time, before=None):
	actions = []
	try:
		if before is not None:
			action_generator = sub_config.subreddit_object.mod.log(limit=None, action='lock', mod=sub_config.bot_username, params={'after':before.id})
		else:
			action_generator = sub_config.subreddit_object.mod.log(limit=None, action='lock', mod=sub_config.bot_username)
	except Exception as e:
		print(sub_config.subreddit_name + " was unable to get mod actions when checking for locked comments with error " + str(e))
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

subnames = [x.split(".")[0] for x in os.listdir("config/")]
for subname in subnames:
	subname = subname.split(".")[0]
	if subname not in ['knife_swap']:
		continue
	print("=== " + subname + " ===")
	sub_config = Config.Config(subname)
	if not sub_config.bot_username or sub_config.disabled:
		print("skipping...")
		continue
	actions = get_mod_actions(sub_config, timestamp)
	print(len(actions))
	for i, action in enumerate(actions):
		if not i%10:
			print(i)
		try:
			body = action.target_body
		except:
			time.sleep(5)
			try:
				body = action.target_body
			except:
				time.sleep(60)
				continue
		if ' -> ' not in body:
			continue
		id = [x for x in action.target_permalink.split('/') if x][-1]
		comment = sub_config.reddit_object.comment(id=id)
		top_comment = comment.parent().parent()
		if top_comment.id not in db[sub_config.subreddit_name]["reddit"]["active"] and top_comment.id not in db[sub_config.subreddit_name]["reddit"]["archived"]:
			print(top_comment.permalink)
			requests.post(request_url + "/add-comment/", {'sub_name': sub_config.subreddit_name, 'platform': 'reddit', 'comment_id': top_comment.id})
