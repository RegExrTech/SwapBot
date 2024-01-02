from Config import Config
from prawcore.exceptions import NotFound
import time
import requests
import swap

WIKI_PAGE_NAME = 'swap_bot_config'

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
			create_wiki_config(config, config_page)
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
	config_page = get_wiki_page(config, WIKI_PAGE_NAME)
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
		invalidate_config(content)
		inform_config_invalid(config_page)
		return
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
	# Dump the new config to the file
	config.dump()
	# Inform parsing successful
	inform_config_valid(config_page)
	# Validate Wiki Page
	validate_wiki_content(config, config_page)

def create_wiki_config(config, config_page):
	validate_wiki_content(config, config_page)
	config_page.mod.update(listed=False, permlevel=2)

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
#	if config.discord_roles:
	content_lines.append("bot_timestamp: " + str(time.time()))  # Must ALWAYS be last
	content = "\n\n".join(content_lines)
	config_page.edit(content=content)

def get_config_content(content):
	config_content = {}
	for line in content.splitlines():
		key = line.split(":")[0]
		value = ":".join(line.split(":")[1:]).strip()
		config_content[key] = value
	return config_content

def invalidate_config(content):
	content = "\n\n".join(content.split("\n\n")[1:] + ["bot_timestamp:" + str(time.time())])
	config_page.edit(content=content)

def inform_config_invalid(config_pag):
	message = "I'm sorry but I was unable to parse the config you set in the " + WIKI_PAGE_NAME + " wiki page. Please review the [config guide](https://www.universalscammerlist.com/config_guide.html) and try again."
	send_update_message(config_page, message)

def inform_config_valid(config_page):
	message = "I have successfully parsed the " + WIKI_PAGE_NAME + " wiki page and updated my config. Thank you for your contribution!"
	send_update_message(config_page, message)

def send_update_message(config_page, message):
	redditor = config_page.revision_by
	username = redditor.name
	message = "Hi u/" + username + "\n\n" + message
	redditor.message(subject=WIKI_PAGE_NAME + " wiki update", message=message)

if __name__ == "__main__":
	import os
	for fname in os.listdir('config'):
		if 'ecigclassifieds' in fname:
			continue
		print("=== " + fname + " ===")
		config = Config(fname.split(".")[0])
#		validate_wiki_content(config, get_wiki_page(config, WIKI_PAGE_NAME))
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
			page.edit(content=content)
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
