import json_helper

class Config():

	def __init__(self, sub_name):
		data = json_helper.get_db("config/"+sub_name+".json")
		self.token = data["token"]
		self.pairing_channel = data["pairing_channel"]
		self.confirmation_channel = data["confirmation_channel"]
		self.log_channel = data["log_channel"]
		self.role_id = data["role_id"]
		self.server_id = data["server_id"]
		self.bot_id = data["bot_id"]
		self.bst_channels = data["bst_channels"]
		self.subreddit_name = data["subreddit_name"]
		self.database_name = self.subreddit_name.lower()
		self.reddit_pairing_config = data["reddit_pairing_config"]
		self.reddit_sub_config = data["reddit_sub_config"]
