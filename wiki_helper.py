from Config import Config
from prawcore.exceptions import NotFound
import time
import requests

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
		config.black_list = [x.strip() for x in config_content["black_list"].split(",")]
		config.black_list = [x for x in config.black_list if x]
		config.black_list = [x[1:] for x in config.black_list if x[0] == "/"]
		config.black_list = [x[2:] for x in config.black_list if x[0] == "u/"]
		config.raw_config["black_list"] = config.black_list
	if "gets_flair_from" in config_content:
		config.gets_flair_from = [x.strip() for x in config_content["gets_flair_from"].split(",")]
		config.gets_flair_from = [x for x in config.gets_flair_from if x]
		config.gets_flair_from = [x[1:] for x in config.gets_flair_from if x[0] == "/"]
		config.gets_flair_from = [x[2:] for x in config.gets_flair_from if x[0] == "r/"]
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
		print(fname)
		config = Config(fname.split(".")[0])
		validate_wiki_content(config, get_wiki_page(config, WIKI_PAGE_NAME))
