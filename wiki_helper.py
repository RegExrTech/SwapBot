import re
from Config import Config
from prawcore.exceptions import NotFound
import time
import requests
import swap
import sys
sys.path.insert(0, 'logger')
import logger

CONFIG_WIKI_PAGE_NAME = 'swap_bot_config'
CONFIRMATIONS_WIKI_PAGE_NAME = "confirmations/{}"

def get_wiki_page(config, wiki_page_name):
	# Get the config page
	try:
		return config.subreddit_object.wiki[wiki_page_name]
	except Exception as e:
		print(e)
		# Transient error, assume no changes have been made
		return None

def get_wiki_page_content(config_page, config):
	# If the config page does not exist, make it
	try:
		return config_page.content_md
	except NotFound as e:
		try:
			create_wiki_page(config, config_page)
			return config_page.content_md
		except NotFound as e:
			print(e)
			# We likely don't have permissions, so just silently return
			return ""
	except Exception as e:
		print(e)
		# Transient error, assume no changes have been made
		return ""

def run_config_checker(config):
	config_page = get_wiki_page(config, CONFIG_WIKI_PAGE_NAME)
	content = get_wiki_page_content(config_page, config)
	if content == "":
		return
	# If the bot was the last person to update the config, break out early
	if config_page.revision_by.name.lower() == config.bot_username.lower():
		return
	# Parse the config page
	try:
		config_content = get_config_content(content)
	except:
		# Unable to parse the config
		invalidate_config(content, config_page, config)
		inform_config_invalid(config_page)
		return
	config_valid = True
	if "flair_word" in config_content:
		config.flair_word = config_content["flair_word"]
		config.raw_config["flair_word"] = config_content["flair_word"]
	if "mod_flair_word" in config_content:
		config.mod_flair_word = config_content["mod_flair_word"]
		config.raw_config["mod_flair_word"] = config_content["mod_flair_word"]
	if "display_mod_count" in config_content:
		config.display_mod_count = config_content["display_mod_count"].lower() == "true"
		config.raw_config["display_mod_count"] = config.display_mod_count
	if "confirmation_text" in config_content:
		config.confirmation_text = config_content["confirmation_text"]
		config.raw_config["confirmation_text"] = config_content["confirmation_text"]
	if "flair_threshold" in config_content:
		try:
			config.flair_threshold = int(config_content["flair_threshold"])
			config.raw_config["flair_threshold"] = config.flair_threshold
		except:
			pass
	if "post_age_threshold" in config_content:
		try:
			config.post_age_threshold = int(config_content["post_age_threshold"])
			config.raw_config["post_age_threshold"] = config.post_age_threshold
		except:
			pass
	if "mod_flair_template" in config_content:
		config.mod_flair_template = config_content["mod_flair_template"]
		config.raw_config["mod_flair_template"] = config_content["mod_flair_template"]
	if "title_black_list" in config_content:
		config.title_black_list = [x.strip() for x in config_content["title_black_list"].split(",")]
		config.title_black_list = [x for x in config.title_black_list if x]
		config.raw_config["title_black_list"] = config.title_black_list
	if "black_list" in config_content:
		black_list = [x.strip() for x in config_content["black_list"].split(",")]
		black_list = [x.lower() for x in black_list if x]
		black_list = [x[1:] if x[0] == "/" else x for x in black_list]
		black_list = [x[2:] if x[0] == "u/" else x for x in black_list]
		users_to_update = [x for x in config.black_list if x not in black_list]
		config.black_list = black_list
		config.raw_config["black_list"] = config.black_list
		for user in users_to_update:
			try:
				redditor = config.reddit_object.redditor(user)
				swap.update_flair(redditor, None, config)
			except Exception as e:
				print("Unable to update flair for u/" + user + " after removing them from the black list for r/" + config.subreddit_display_name + " with error " + str(e))
	if "gets_flair_from" in config_content:
		config.gets_flair_from = [x.strip() for x in config_content["gets_flair_from"].split(",")]
		config.gets_flair_from = [x for x in config.gets_flair_from if x]
		config.gets_flair_from = [x[1:] if x[0] == "/" else x for x in config.gets_flair_from]
		config.gets_flair_from = [x[2:] if x[0] == "r/" else x for x in config.gets_flair_from]
		config.raw_config["gets_flair_from"] = config.gets_flair_from
	if "booster_check_count_threshold" in config_content:
		try:
			config.booster_check_count_threshold = int(config_content['booster_check_count_threshold'])
			config.raw_config['booster_check_count_threshold'] = config.booster_check_count_threshold
		except:
			pass
	if "booster_check_hours_threshold" in config_content:
		try:
			config.booster_check_hours_threshold = int(config_content['booster_check_hours_threshold'])
			config.raw_config['booster_check_hours_threshold'] = config.booster_check_hours_threshold
		except:
			pass
	if "booster_check_max_score" in config_content:
		try:
			config.booster_check_max_score = int(config_content['booster_check_max_score'])
			config.raw_config['booster_check_max_score'] = config.booster_check_max_score
		except:
			pass
	if "comment_validator" in config_content:
		try:
			re.compile(config_content['comment_validator'])
			config.comment_validator = config_content['comment_validator']
			config.raw_config['comment_validator'] = config_content['comment_validator']
		except re.error:
			config_valid = False

	# Dump the new config to the file
	config.dump()
	# Inform parsing successful
	if config_valid:
		inform_config_valid(config_page)
	else:
		inform_config_invalid(config_page)
	# Validate Wiki Page
	validate_wiki_content(config, config_page)

def create_wiki_page(config, page):
	if page.name == CONFIG_WIKI_PAGE_NAME:
		validate_wiki_content(config, page)
		permlevel=2
	else:
		edit_wiki_page(page, "", config)
		permlevel=1
	page.mod.update(listed=False, permlevel=permlevel)

def validate_wiki_content(config, config_page):
	content_lines = []
	content_lines.append("For help with this configuration, please visit https://redd.it/yixgoa")  # Must ALWAYS be first
	content_lines.append("flair_word: " + config.flair_word)
	content_lines.append("mod_flair_word: " + config.mod_flair_word)
	content_lines.append("display_mod_count: " + str(config.display_mod_count))
	content_lines.append("confirmation_text: " + config.confirmation_text)
	content_lines.append("flair_threshold: " + str(config.flair_threshold))
	content_lines.append("post_age_threshold: " + str(config.post_age_threshold))
	content_lines.append("mod_flair_template: " + config.mod_flair_template)
	content_lines.append("title_black_list: " + ",".join(config.title_black_list))
	content_lines.append("black_list: " + ",".join(config.black_list))
	content_lines.append("gets_flair_from: " + ",".join(config.gets_flair_from))
	content_lines.append("booster_check_count_threshold: " + str(config.booster_check_count_threshold))
	content_lines.append("booster_check_hours_threshold: " + str(config.booster_check_hours_threshold))
	content_lines.append("booster_check_max_score: " + str(config.booster_check_max_score))
	content_lines.append("comment_validator: " + config.comment_validator)
#	if config.discord_roles:
	content_lines.append("bot_timestamp: " + str(time.time()))  # Must ALWAYS be last
	content = "\n\n".join(content_lines)
	edit_wiki_page(config_page, content, config)

def get_config_content(content):
	config_content = {}
	for line in content.splitlines():
		key = line.split(":")[0]
		value = ":".join(line.split(":")[1:]).strip()
		config_content[key] = value
	return config_content

def edit_wiki_page(page, content, config):
	try:
		page.edit(content=content)
	except:
		time.sleep(5)
		try:
			page.edit(content=content)
		except Exception as e:
			logger.log("Failed to update wiki page https://www.reddit.com/r/" + config.subreddit_name + "/wiki/" + page.name, e)
			time.sleep(60)

def update_confirmation_page(username, content, overview_content, sub_config):
	if content:
		page = get_wiki_page(sub_config, CONFIRMATIONS_WIKI_PAGE_NAME.format(username))
		if page is not None:
			# Makes page if one does not exist
			get_wiki_page_content(page, sub_config)
			edit_wiki_page(page, content, sub_config)
	if overview_content:
		# Update the overview page
		logger_config = Config("logger")
		page = get_wiki_page(logger_config, CONFIRMATIONS_WIKI_PAGE_NAME.format(username))
		if page is not None:
			old_overview_content = get_wiki_page_content(page, logger_config)
			old_overview_lines = old_overview_content.split("\n")
			# Replace the old content with the new if there is any overlap.
			overview_lines = [overview_content] + [x for x in old_overview_lines if not x.endswith("r/" + sub_config.subreddit_name)]
			# Then filter out any lines with no interesting information.
			overview_lines = [x for x in overview_lines if not x.startswith("* [0") and x]
			# Sort by highest to lowest so we're consistent and we can check for changes more easily.
			overview_lines.sort(key = lambda x: int(x.split(" ")[1].split("[")[-1]))
			overview_lines = overview_lines[::-1]
			new_content = "\n".join(overview_lines)
			# Only make a network call if we're actually making update.
			if new_content != old_overview_content:
				edit_wiki_page(page, new_content, sub_config)

def invalidate_config(content, config_page, sub_config):
	content = "\n\n".join(content.split("\n\n")[:-1] + ["bot_timestamp: " + str(time.time())])
	edit_wiki_page(config_page, content, sub_config)

def inform_config_invalid(config_page):
	message = "I'm sorry but I was unable to parse the config you set in the " + CONFIG_WIKI_PAGE_NAME + " wiki page. Please review the [config guide](https://www.reddit.com/r/RegExrSwapBot/comments/yixgoa/swap_bot_config_guide/) and try again."
	send_update_message(config_page, message)

def inform_config_valid(config_page):
	message = "I have successfully parsed the " + CONFIG_WIKI_PAGE_NAME + " wiki page and updated my config. Thank you for your contribution!"
	send_update_message(config_page, message)

def send_update_message(config_page, message):
	redditor = config_page.revision_by
	username = redditor.name
	message = "Hi u/" + username + "\n\n" + message
	redditor.message(subject=CONFIG_WIKI_PAGE_NAME + " wiki update", message=message)

if __name__ == "__main__":
	import os
	for fname in os.listdir('config'):
		if 'ecigclassifieds' in fname:
			continue
		sub_config = Config(fname.split(".")[0])
		if not sub_config.bot_username or sub_config.disabled:
			continue
		print("=== " + fname + " ===")
		validate_wiki_content(sub_config, get_wiki_page(sub_config, CONFIG_WIKI_PAGE_NAME))
#		sub_config.dump()

def _modify_automod():
	for fname in os.listdir('config'):
		page = get_wiki_page(config, 'config/automoderator')
		content = get_wiki_page_content(page, config)
		for rule in content.split("---"):
			if 'account_age:' in rule or 'karma:' in rule:
				lines = rule.splitlines()
				for line in lines:
					if '#' in line:
						continue
#					if 'account_age:' in line or 'karma:' in line:
#						print("    " + line.strip())
#				print('---')
		if config.subreddit_name in ["animalcrossingamiibos", "discexchange", "ulgeartrade", "canadianknifeswap", "ygomarketplace", "fragrancemarketplace", "airsoftmarketcanada", "photomarket", "disneywishables", "synths4sale", "boardgameexchange"]:
			content += "\n\n---\n\n"
			content += 'author:\n    account_age: "<7 days"\n    comment_karma: "<10"\n    is_contributor: false\n    satisfy_any_threshold: true\n    \naction: remove\naction_reason: new account removal\nmessage_subject: PLEASE READ THE ENTIRE MESSAGE from r/' + config.subreddit_name + '\nmessage: |    \n    {{author}} - Your most recent post on /r/' + config.subreddit_name + ' has been removed because we require that our users have an established reddit account **AND** that they are **active** reddit participants. Either your account is too young **or** you do not make posts/comments often enough on reddit **as a whole** (*not just on r/' + config.subreddit_name + '*). We understand this can be frustrating but it is for the overall good of the community. Please consider participating more in reddit as a whole before posting in our community again. This is an automated process so once you participate more on reddit, you will automatically be able to post here. Thanks for your understanding. Please try commenting or posting again in r/' + config.subreddit_name + ' later to see if you meet the requirements.'
			edit_wiki_page(page, content, config)
		if config.subreddit_name in ["coffee_exchange", "watchexchangecanada", "animalcrossingamiibos", "discexchange", "ulgeartrade", "canadianknifeswap", "ygomarketplace", "fragrancemarketplace", "airsoftmarketcanada", "photomarket", "disneywishables", "synths4sale", "boardgameexchange"]:
			# send message
			message = "Hello r/" + config.subreddit_name + " mods. This is a brief message to let you know that your automod rules have been automatically updated. Specifically, a rule has been added to introduce an age and karma filter to your community.\n\nThere has been an increase in scammers using low-requirement communities like yours to boost their flair score with brand new accounts, then using that 'feedback' to convince folks to send them money via unsafe methods. Because of the flair sharing feature, some subs are seeing users with artifically boosters scores appearing in their own subs due to the lack of restrictions in your sub. Other subs are just seeing scammers point to flair on subs like yours as a reference.\n\nWhile this change was added without input from the mod team, it is now entirely in your hands to modify or remove it. You can view your automod config [here](https://www.reddit.com/r/" + config.subreddit_name + "/wiki/config/automoderator/) and find the rule at the very bottom of the config page. If you wish to remove the rule, simply delete everything after the `---` characters at the bottom of the wiki page. If you wish to change the age and karma filter, simply adjust the numbers to your liking.\n\nIf you wish to keep the rule but allow users to participate in your community who do not meet the requirements, you can add them as approved submitters. You can do this via mod mail by clicking 'Approve User' under their name in a message they send you. This will allow you to keep the filter while still allowing good-faith members to participate.\n\nI'll be monitoring this message thread, so please let me know if you have any questions!\n\nBest,\n\nu/RegExr"
			try:
				config.subreddit_object.message("Swap Bot Update - Automod Filters Adjusted", message)
			except Exception as e:
				print("Unable to send mod mail to r/" + config.subreddit_name + " with error " + str(e))
		else:
			message = "Hello r/" + config.subreddit_name + " mods. This is a brief message to let you know that all subs using this Swap Bot system have been audited for age and karma restrictions.\n\nIf you're seeing this message, this means that your sub had sufficient requirements to participate in your sub and no action was taken. However, this message is still being sent to inform you that the subs without proper restrictions have been updated to include some baseline restrictions. This may be relevant to you as scammers have been boosting their flair score on unrestricted subs and using that to gain influence and scam users on more active subs. This manifested either as users just pointing to their flair on other subs or, in the case of subs that share flair with other subs, actual changes in flair on your sub based on these boosted transactions scores.\n\nTo reiterate, these scammers were able to easily get through due to the lack of age/karma restrictions from some subs. This has since been fixed. However, I am working on updating the bot to perform a cross-sub analysis whenever a transaction is confirmed to try and detect deeper levels of flair boosting to prevent scammers. I'll send another update once this work is done.\n\nThank you to those of you who have helped me chase down these types of users in the past. There haven't been many of them, but one is more than enough to warrent changes. I'll be monitoring this thread, so please let me know if you have any questions.\n\nBest,\n\nu/RegExr"
			try:
				config.subreddit_object.message("Swap Bot Update - Increased Fraud Prevention", message)
			except Exception as e:
				print("Unable to send mod mail to r/" + config.subreddit_name + " with error " + str(e))
