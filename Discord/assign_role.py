import requests

roleURL = "https://discordapp.com/api/guilds/{}/members/{}/roles/{}"

def assign_role(server_id, discord_user_id, role_id, bot_token):
	headers = {"Authorization":"Bot {}".format(bot_token),
		"User-Agent":"SwapBot (https://www.regexr.tech, v0.1)",
		"Content-Type":"application/json"}
	requests.put(roleURL.format(server_id, discord_user_id, role_id), headers=headers)
