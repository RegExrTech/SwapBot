import requests
import json_helper

TOKENS = json_helper.get_db("Discord/tokens.json")

headers = {"Authorization":"Bot {}".format(TOKENS["token"]),
        "User-Agent":"SwapBot (https://www.regexr.tech, v0.1)",
        "Content-Type":"application/json"}

roleURL = "https://discordapp.com/api/guilds/{}/members/{}/roles/{}"

def assign_role(server_id, discord_user_id, role_id):
	requests.put(roleURL.format(server_id, discord_user_id, role_id), headers=headers)
