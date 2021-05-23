import requests
import json_helper

TOKENS = json_helper.get_db("Discord/tokens.json")

headers = {"Authorization":"Bot {}".format(TOKENS["token"]),
        "User-Agent":"SwapBot (https://www.regexr.tech, v0.1)",
        "Content-Type":"application/json"}

roleURL = "https://discordapp.com/api/guilds/{}/members/{}/roles/{}"

def assign_role(server_id, discord_user_id, role_id):
	print("Would have assigned discord role " + role_id + " to discord user " + discord_user_id + " on server " + server_id)
	return
	requests.put(roleURL.format(server_id, discord_user_id, role_id), headers=headers)


 # 691788886367535224
