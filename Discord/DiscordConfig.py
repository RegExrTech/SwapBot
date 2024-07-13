import json_helper

class Config():

	def __init__(self, sub_name):
		data = json_helper.get_db("Discord/config/"+sub_name+".json")
		self.token = data["token"]
		self.pairing_channel = data["pairing_channel"]
		self.confirmation_channel = data["confirmation_channel"]
		self.log_channel = data["log_channel"]
		self.role_id = data["role_id"]
		self.feedback_check_channel = data["feedback_check_channel"]
		self.server_id = data["server_id"]
		self.bot_id = data["bot_id"]
		self.bst_channels = data["bst_channels"]
		self.reddit_pairing_config = data["reddit_pairing_config"]
		self.bareUrl = "https://discordapp.com/api/channels/{}/messages"
		self.baseUrl = self.bareUrl.format(self.confirmation_channel)
		self.feedbackUrl = self.bareUrl.format(self.feedback_check_channel)
		self.bst_channel_url = "https://discordapp.com/api/channels/{}/messages/{}"
		self.headers = {"Authorization":"Bot {}".format(self.token), "User-Agent":"SwapBot (https://www.regexr.tech, v0.1)", "Content-Type":"application/json"}
