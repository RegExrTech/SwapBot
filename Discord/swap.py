import time
import json_helper
import requests
import re
import json
import praw

time_limit_minutes = 30
time_limit = time_limit_minutes * 60 # Seconds

bot_username = "Swap Bot#0749"
TOKENS = json_helper.get_db("tokens.json")

reddit = praw.Reddit(client_id=TOKENS['Reddit']['client_id'], client_secret=TOKENS['Reddit']['client_secret'], user_agent='Swap Bot for Account Linking v1.0 (by u/RegExr)', username=TOKENS['Reddit']['username'], password=TOKENS['Reddit']['password'])

baseURL = "https://discordapp.com/api/channels/{}/messages".format(TOKENS["channel"])
roleURL = "https://discordapp.com/api/guilds/" + TOKENS['server_id'] + "/members/{}/roles/{}"
headers = {"Authorization":"Bot {}".format(TOKENS["token"]),
	"User-Agent":"SwapBot (https://www.regexr.tech, v0.1)",
	"Content-Type":"application/json"}


def get_username_from_text(text, usernames_to_ignore=[]):
	pattern = re.compile("(u\/[A-Za-z0-9_-]+)")
	found = re.findall(pattern, text)
	username = ""
	for found_username in found:
		if found_username not in [x.lower() for x in usernames_to_ignore]:
			username = found_username
			break
	return username

def get_reddit_messages(reddit):
	messages = []
	to_mark_as_read = []
	try:
		for message in reddit.inbox.unread():
			to_mark_as_read.append(message)
			if not message.was_comment:
				messages.append(message)
	except Exception as e:
		print(e)
		print("Failed to get next message from unreads. Ignoring all unread messages and will try again next time.")

	for message in to_mark_as_read:
		try:
			message.mark_read()
		except Exception as e:
			print(e)
			print("Unable to mark message as read. Leaving it as is.")
	return messages


r = requests.get(baseURL, headers = headers)
messages = r.json()

pending_requests = json_helper.get_db("pending_requests.json")
paired_usernames = json_helper.get_db("paired_usernames.json")

# Check Discord for messages
for message in messages:
	discord_username = message['author']['username'] + "#" + message['author']['discriminator']
	discord_user_id = message['author']['id']
	# If the message is from the bot, skip
	if discord_username == bot_username:
		continue
	# If the message is from a user with a completed or pending request, skip
	if discord_username in pending_requests or discord_username in paired_usernames['discord']:
		continue
	body = message['content']
	reddit_username = get_username_from_text(body)
	discord_message_id = message['id']
	# If we were able to find a reddit username in the message
	if reddit_username:
		# Try to send a PM via reddit
		try:
			reddit.redditor(reddit_username.split("/")[-1]).message("Please Confirm Your Identity", "A request has been sent from " + discord_username + " on discord to link that account with your Reddit account. If you authorized this request, please reply to this message.\n\n##If you did **NOT** authorize this request, please **ignore this message.**\n\nThanks!")
			reddit_message = reddit.inbox.sent(limit=1).next()
			reddit_message_id = reddit_message.id
			reply_text = "Sending a message to " + reddit_username + " on Reddit. Please respond to the bot via Reddit to confirm your identity. If you do not reply within " + str(time_limit_minutes) + " minutes, you will need to restart this process."
			pending_requests[discord_username] = {"reddit_username": reddit_username, "request_timestamp": time.time(), 'reddit_message_id': reddit_message_id, "discord_user_id": discord_user_id}
		# If we fail, tell them to try again later
		except:
			reply_text = "Sorry, I was unable to send a message to that username. Please check your spelling and try again."
		reply_data = {'content': reply_text, 'message_reference': {'message_id': discord_message_id}}
		r = requests.post(baseURL, headers=headers, data=json.dumps(reply_data))

# Delete any stale requests
for discord_username, data in pending_requests.items():
	if data['request_timestamp'] + time_limit < time.time():
		del(pending_requests[discord_username])

# Check Reddit for unread replies
reddit_messages = get_reddit_messages(reddit)
for reddit_message in reddit_messages:
	reddit_message_id = reddit_message.parent_id.split("_")[-1]
	for discord_username, data in pending_requests.items():
		if not reddit_message_id == data['reddit_message_id']:
			continue
		paired_usernames['discord'][discord_username] = data['reddit_username']
		paired_usernames['reddit'][data['reddit_username']] = discord_username
		try:
			reddit_message.reply("Thank you for confirming your identity. Your discord account is now linked to your reddit account.")
		except:
			pass
		requests.put(roleURL.format(data['discord_user_id'], TOKENS['role_id']), headers=headers)
		del(pending_requests[discord_username])

# Dump the relevant databases
json_helper.dump(pending_requests, "pending_requests.json")
json_helper.dump(paired_usernames, "paired_usernames.json")
