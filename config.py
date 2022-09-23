import os
import json
import sys
sys.path.insert(0, "Discord")
from DiscordConfig import Config as DiscordConfig

def ascii_encode_dict(data):
        ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
        return dict(map(ascii_encode, pair) for pair in data.items())

def get_json_data(fname):
        with open(fname) as json_data:
                data = json.load(json_data, object_hook=ascii_encode_dict)
        return data

class Config():

	def __init__(self, sub_name):
		f = open("config/" + sub_name.lower() + "-config.txt", "r")
		info = f.read().splitlines()
		f.close()

		config = {}
		for line in info:
			key = line.split(":")[0].lower()
			value = ":".join(line.split(":")[1:])
			config[key] = value

		self.subreddit_name = config['subreddit_name'].lower()
		self.subreddit_display_name = config['subreddit_name']
		self.database_name = self.subreddit_name.lower()
		self.client_id = config['client_id']
		self.client_secret = config['client_secret']
		self.bot_username = config['bot_username']
		self.bot_password = config['bot_password']
		self.flair_word = config['flair_word']
		self.mod_flair_word = config['mod_flair_word']
		if not self.mod_flair_word.strip():
			self.mod_flair_word = ""
		if config['display_mod_count'].lower() == "true":
			self.display_mod_count = True
		else:
			self.display_mod_count = False
		if config['flair_templates'].lower() == "true":
			self.flair_templates = get_json_data('templates/'+self.subreddit_name+'.json')
		else:
			self.flair_templates = False
		self.confirmation_text = config['confirmation_text']
		if not self.confirmation_text:
			self.confirmation_text = "Added"
		self.flair_threshold = int(config['flair_threshold'])
		self.post_age_threshold = float(config['post_age_threshold'])
		self.mod_flair_template = config['mod_flair_template']
		if config['titles'].lower() == "true":
			self.titles = get_json_data('titles/'+self.subreddit_name+'.json')
		else:
			self.titles = False
		if config['age_titles'].lower() == "true":
			self.age_titles = get_json_data('age_titles/'+self.subreddit_name+'.json')
		else:
			self.age_titles = False
		self.title_blacklist = [x for x in config['title_black_list'].split(",") if x]
		self.blacklisted_users = [x for x in config['black_list'].split(",") if x]
		self.gets_flair_from = self.get_gets_flair_from([x.lower() for x in config['gets_flair_from'].split(",") if x])
		self.gives_flair_to = self.get_gives_flair_to(self.subreddit_name)
		self.sister_subs = {}
		if config['discord_config'].lower() == "true":
			self.discord_config = DiscordConfig(self.subreddit_name)
		else:
			self.discord_config = None
		if config['discord_roles'].lower() == "true":
			self.discord_roles = get_json_data('roles/'+self.subreddit_name+'.json')
		else:
			self.discord_roles = False
		self.discord_mod_contact_text = config['discord_mod_contact_text']

	def get_gets_flair_from(self, initial_list):
		gets_flair_from = []
		if not initial_list:
			return gets_flair_from
		if initial_list[0] == "*":
			for fname in os.listdir('config'):
				f = open("config/"+fname, "r")
				lines = f.read().splitlines()
				f.close()
				d = {}
				for line in lines:
					d[line.split(":")[0]] = line.split(":")[1]
				if d["subreddit_name"] in initial_list:
					continue
				if d["subreddit_name"] == self.subreddit_name:
					continue
				gets_flair_from.append(d['subreddit_name'])
		else:
			gets_flair_from = initial_list
		return gets_flair_from

	def get_gives_flair_to(self, sub_name):
		gives_flair_to = []
		sub_names = []
		for fname in os.listdir('config'):
			f = open("config/"+fname, "r")
			lines = f.read().splitlines()
			f.close()
			d = {}
			for line in lines:
				d[line.split(":")[0]] = line.split(":")[1]
			if d['subreddit_name'] == self.subreddit_name:
				continue
			sub_names.append(d['subreddit_name'])
			d['gets_flair_from'] = d['gets_flair_from'].split(",")
			# If the sub has a wildcard, and sub names following the wild card are excluded.
			# If a sub does not have a wildcard, any sub explicitly listed is included.
			# If a sub ONLY has a wildcard, ALL subs are included.
			if (d['gets_flair_from'][0] == "*" and sub_name not in d['gets_flair_from']) or (sub_name in d['gets_flair_from'] and not d['gets_flair_from'][0] == "*"):
				gives_flair_to.append(sub_names[-1])
		return gives_flair_to
