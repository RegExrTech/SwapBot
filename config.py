import json

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

		self.subreddit_name = config['subreddit_name']
		self.database_name = self.subreddit_name.lower()
		self.client_id = config['client_id']
		self.client_secret = config['client_secret']
		self.bot_username = config['bot_username']
		self.bot_password = config['bot_password']
		self.flair_word = " " + config['flair_word']
		self.mod_flair_word = config['mod_flair_word'] + " "
		if not self.mod_flair_word.strip():
			self.mod_flair_word = ""
		if config['flair_templates'].lower() == "true":
			self.flair_templates = get_json_data('templates/'+self.subreddit_name+'.json')
		else:
			self.flair_templates = False
		self.confirmation_text = config['confirmation_text']
		if not self.confirmation_text:
			self.confirmation_text = "Added"
		self.flair_threshold = int(config['flair_threshold'])
		self.mod_flair_template = config['mod_flair_template']
		if config['titles'].lower() == "true":
			self.titles = get_json_data('titles/'+self.subreddit_name+'.json')
		else:
			self.titles = False
		if config['age_titles'].lower() == "true":
			self.age_titles = get_json_data('age_titles/'+self.subreddit_name+'.json')
		else:
			self.age_titles = False
		self.blacklisted_users = [x for x in config['black_list'].split(",") if x]
		self.gets_flair_from = [x.lower() for x in config['gets_flair_from'].split(",") if x]
		self.gives_flair_to = [x.lower() for x in config['gives_flair_to'].split(",") if x]
		self.sister_subs = {}
