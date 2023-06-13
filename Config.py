import os
import json
import sys
sys.path.insert(0, "Discord")
from DiscordConfig import Config as DiscordConfig
import praw

def get_json_data(fname):
	with open(fname) as json_data:
		data = json.load(json_data)
	return data

class Config():

	def __init__(self, sub_name):
		self.fname = "config/" + sub_name.lower() + ".json"
		self.raw_config = get_json_data(self.fname)

		self.subreddit_name = self.raw_config['subreddit_name'].lower()
		self.subreddit_display_name = self.raw_config['subreddit_name']
		self.database_name = self.subreddit_name.lower()
		self.client_id = self.raw_config['client_id']
		self.client_secret = self.raw_config['client_secret']
		self.bot_username = self.raw_config['bot_username']
		self.bot_password = self.raw_config['bot_password']
		self.refresh_token = self.raw_config['refresh_token']
		self.reddit_object = praw.Reddit(client_id=self.client_id, client_secret=self.client_secret, user_agent='Swap Bot for ' + self.subreddit_name + ' v1.0 (by u/RegExr)', refresh_token=self.refresh_token)
		self.subreddit_object = self.reddit_object.subreddit(self.subreddit_name)
		self.flair_word = self.raw_config['flair_word']
		self.mod_flair_word = self.raw_config['mod_flair_word']
		self.display_mod_count = self.raw_config['display_mod_count']
		self.flair_templates = self.raw_config['flair_templates']
		self.confirmation_text = self.raw_config['confirmation_text']
		if not self.confirmation_text:
			self.confirmation_text = "Added"
		self.flair_threshold = self.raw_config['flair_threshold']
		self.post_age_threshold = self.raw_config['post_age_threshold']
		self.mod_flair_template = self.raw_config['mod_flair_template']
		self.titles = self.raw_config['titles']
		self.age_titles = self.raw_config['age_titles']
		self.title_black_list = [x.lower() for x in self.raw_config['title_black_list']]
		self.black_list = [x.lower() for x in self.raw_config['black_list']]
		self.gets_flair_from = self.get_gets_flair_from([x.lower() for x in self.raw_config['gets_flair_from']])
		self.gives_flair_to = self.get_gives_flair_to(self.subreddit_name)
		self.sister_subs = {}
		if self.raw_config['discord_config']:
			self.discord_config = DiscordConfig(self.subreddit_name)
		else:
			self.discord_config = None
		self.discord_roles = self.raw_config['discord_roles']
		self.discord_mod_contact_text = self.raw_config['discord_mod_contact_text']

	def get_gets_flair_from(self, initial_list):
		gets_flair_from = []
		if not initial_list:
			return gets_flair_from
		if initial_list[0] == "*":
			for fname in os.listdir('config'):
				raw_config = get_json_data("config/"+fname)
				if raw_config["subreddit_name"] in initial_list:
					continue
				if raw_config["subreddit_name"] == self.subreddit_name:
					continue
				gets_flair_from.append(raw_config['subreddit_name'])
		else:
			gets_flair_from = initial_list
		return gets_flair_from

	def get_gives_flair_to(self, sub_name):
		gives_flair_to = []
		for fname in os.listdir('config'):
			if '.swp' in fname:
				continue
			raw_config = get_json_data("config/"+fname)
			if raw_config['subreddit_name'] == self.subreddit_name:
				continue
			if not raw_config['gets_flair_from']:
				continue
			# If the sub has a wildcard, and sub names following the wild card are excluded.
			# If a sub does not have a wildcard, any sub explicitly listed is included.
			# If a sub ONLY has a wildcard, ALL subs are included.
			if (raw_config['gets_flair_from'][0] == "*" and sub_name not in raw_config['gets_flair_from']) or (sub_name in raw_config['gets_flair_from'] and not raw_config['gets_flair_from'][0] == "*"):
				gives_flair_to.append(raw_config['subreddit_name'])
		return gives_flair_to

	def dump(self):
		fname = "config/" + self.subreddit_name.lower() + ".json"
		with open(fname, 'w') as outfile:  # Write out new data
			outfile.write(json.dumps(self.raw_config, sort_keys=True, indent=4))
