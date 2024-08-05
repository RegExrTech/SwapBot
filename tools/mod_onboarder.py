import os
import time
import sys
sys.path.insert(0, ".")
sys.path.insert(0, "logger")
import Config
import logger
import swap

f_path = 'database/mods.txt'

if not os.path.exists(f_path):
	os.mknod(f_path)

f = open(f_path, 'r')
already_sent = set(f.read().splitlines())
f.close()

title = "[PLEASE READ] RegExrSwapBot Usage Guide"

subnames = [x.split(".")[0] for x in os.listdir("config/")]
for subname in subnames:
	if subname == 'funkoppopmod':
		continue
	sub_config = Config.Config(subname)
	if not sub_config.bot_username or sub_config.disabled:
		continue
	try:
		mod_list = sub_config.subreddit_object.moderator()
	except:
		print("    Unable to get mod list from r/" + subname)
		continue
	# Wait until the bot is a mod of the sub to send messages
	if sub_config.bot_username.lower() not in [x.name.lower() for x in mod_list]:
		continue
	body = "Hi there! If you're receiving this message, it means that either you have joined r/" + subname + " as a new moderator or r/" + subname + " has just started participating in the RegExr Swap Bot.\n\n"
	body += "If you're new to using the Swap Bot as a moderator, please review the [usage guide](https://www.reddit.com/r/RegExrSwapBot/comments/ykaav1/example_usage_guide/) and [config guide](https://www.reddit.com/r/RegExrSwapBot/comments/yixgoa/swap_bot_config_guide/) as soon as possible. They give details on how the bot should work and how to configure the bot, respectively. Please ensure you're familiar with how the bot works so you can answer questions that arise in mod mail.\n\n"
	body += "If you have any questions, please reach out to u/RegExr.\n\n"
	body += "Thank you so much for your help and participation!"
	for mod in mod_list:
		mod_name = mod.name.lower()
		if mod_name in already_sent:
			continue
		if 'uslbot' in mod_name or 'automod' in mod_name:
			continue
		if 'bot' == mod_name[-3:]:
			continue
		try:
			mod.message(subject=title, message=body)
		except Exception as e:
			logger.log("  Unable to send message to u/" + mod_name + " on sub r/" + subname + " with error " + str(e))
			time.sleep(60)
		logger.log("Found a new mod! User is u/" + mod_name + " from r/" + subname)
		already_sent.add(mod_name)
		swap.update_flair(sub_config.reddit_object.redditor(mod_name), None, sub_config)
		# Do this every time we find a new mod, rather than at the end, so overlapping scripts don't send the same message twice.
		f = open(f_path, 'w')
		already_sent = list(already_sent)
		already_sent.sort()
		f.write("\n".join(already_sent))
		f.close()
		already_sent = set(already_sent)

