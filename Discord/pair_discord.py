import time
import json_helper
import requests
import re
import json
import praw
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('sub_name', metavar='C', type=str)
args = parser.parse_args()

time_limit_minutes = 30
time_limit = time_limit_minutes * 60 # Seconds

request_url = "http://0.0.0.0:8000"

bot_username = "Swap Bot#0749"
TOKENS = json_helper.get_db("Discord/config/" + args.sub_name + ".json")

reddit = praw.Reddit(client_id=TOKENS['reddit_pairing_config']['client_id'], client_secret=TOKENS['reddit_pairing_config']['client_secret'], user_agent='Swap Bot for Account Linking v1.0 (by u/RegExr)', refresh_token=TOKENS['reddit_pairing_config']['refresh_token'])

baseURL = "https://discordapp.com/api/channels/{}/messages".format(TOKENS["pairing_channel"])
logBaseURL = "https://discordapp.com/api/channels/{}/messages".format(TOKENS["log_channel"])
roleURL = "https://discordapp.com/api/guilds/" + TOKENS['server_id'] + "/members/{}/roles/{}"
deleteMessageURL = "https://discordapp.com/api/channels/{}/messages/{}"
headers = {"Authorization":"Bot {}".format(TOKENS["token"]),
	"User-Agent":"SwapBot (https://www.regexr.tech, v0.1)",
	"Content-Type":"application/json"}

reddit_message_subject = "Please Confirm Your Identity on the " + args.sub_name + " discord server"

def decode(text):
	try:
		return text.encode('utf-8').decode('utf-8').encode('ascii', 'ignore').replace("\u002F", "/")
	except:
		try:
			return text.decode('utf-8').encode('ascii', 'ignore').replace("\u002F", "/")
		except Exception as e:
			return text.decode('cp1252').encode('ascii', 'ignore').replace("\u002F", "/")

def get_username_from_text(text, usernames_to_ignore=[]):
	pattern = re.compile("u\/([A-Za-z0-9_-]+)")
	found = re.findall(pattern, text.lower())
	username = ""
	for found_username in found:
		found_username = found_username.lower()
		if found_username not in [x.lower() for x in usernames_to_ignore]:
			username = found_username
			break
	return username

def get_reddit_messages(reddit):
	messages = []
	to_mark_as_read = []
	try:
		for message in reddit.inbox.unread():
			if reddit_message_subject not in str(message.subject):
				continue
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

def send_reddit_message(reddit_username, discord_username, reddit, time_limit_minutes, pending_requests, discord_user_id, discord_message_id):
	reddit.redditor(reddit_username).message(reddit_message_subject, "A request has been sent from " + discord_username + " on discord to link that account with your Reddit account. If you authorized this request, please reply to this message.\n\n##If you did **NOT** authorize this request, please **ignore this message.**\n\nThanks!")
	inbox = reddit.inbox.sent(limit=None)
	reddit_message_id = None
	while not reddit_message_id:
		reddit_message = inbox.next()
		if str(reddit_message.subject) == reddit_message_subject:
			reddit_message_id = reddit_message.id
	reply_text = "Sending a message to u/" + reddit_username + " on Reddit. Please respond to the bot via Reddit to confirm your identity. If you do not reply within " + str(time_limit_minutes) + " minutes, you will need to restart this process."
	requests.post(request_url + "/add-account-pairing-request/", data={"discord_user_id": discord_user_id, "reddit_username": reddit_username, "request_timestamp": time.time(), 'reddit_message_id': reddit_message_id, 'discord_message_id': discord_message_id})
	return reply_text


r = requests.get(baseURL, headers = headers)
messages = r.json()

pending_requests = requests.get(request_url + "/get-pending-account-pairing-requests/").json()
paired_usernames = requests.get(request_url + "/get-paired-usernames/").json()

to_skip = []

# Check Discord for messages
for message in messages:
	discord_username = message['author']['username'] + "#" + message['author']['discriminator']
	discord_username = decode(discord_username.lower())
	discord_user_id = message['author']['id']
	discord_message_id = message['id']

	if discord_message_id in to_skip:
		continue
	# If we find a message from the bot and the bot was replying to someone, add that reply to a list of messages to skip over
	if 'message_reference' in message and message['message_reference'] and discord_user_id == TOKENS["bot_id"]:
		to_skip.append(message['message_reference']['message_id'])
		continue
	# If the message is from a user with a pending request, skip
	if discord_user_id in pending_requests:
		continue

	body = message['content']
	# If the message is from a user with a completed request, let them know and make sure the role is applied
	if discord_user_id in paired_usernames['discord']:
		reddit_username = None
	else:
		reddit_username = get_username_from_text(body)

	reply_text = ""
	# If we were able to find a reddit username in the message
	if reddit_username is not None and reddit_username:
		# If the reddit username in question has already been paired:
		if reddit_username in paired_usernames['reddit']:
			reply_text = "Sorry, this Reddit account was already used to pair with a different discord account. Specifically, it is paired to <@" + str(paired_usernames['reddit'][reddit_username]['discord'] + ">.")
		else:
			# Try to send a PM via reddit
			try:
				reply_text = send_reddit_message(reddit_username, discord_username, reddit, time_limit_minutes, pending_requests, discord_user_id, discord_message_id)
			# If we fail, tell them to try again later
			except Exception as e:
				error_text = str(e)
				if "RATELIMIT" in error_text:
					if 'minute' in error_text:
						time_to_sleep = int(error_text.split("Take a break for ")[1].split(" minute")[0]) * 60
					else:
						time_to_sleep = int(error_text.split("Take a break for ")[1].split(" second")[0])
					time.sleep(time_to_sleep + 2)
					try:
						reply_text = send_reddit_message(reddit_username, discord_username, reddit, time_limit_minutes, pending_requests, discord_user_id, discord_message_id)
					except Exception as e:
						print(e)
						reply_text = "Sorry, I was unable to send a message to that username. Please check your spelling and try again."
				else:
					print(e)
					reply_text = "Sorry, <@" + str(discord_user_id) + ">, I was unable to send a message to that username. Please check your spelling and try again."
	elif reddit_username is not None and not reddit_username:
		reply_text = "Sorry, I was unable to detect a reddit username in your message. Please send another message, ensuring that the reddit usernames begin with u/. Thanks!"
	else:
		reply_text = "Your account has already been verified so I've added the relevant role to your account. Thanks!"
		requests.put(roleURL.format(discord_user_id, TOKENS['role_id']), headers=headers)

	reply_data = {'content': reply_text, 'message_reference': {'message_id': discord_message_id}}
	requests.post(baseURL, headers=headers, data=json.dumps(reply_data))

# Delete any stale requests
for discord_user_id, data in pending_requests.items():
	if data['request_timestamp'] + time_limit < time.time():
		reply_text = "<@" + str(discord_user_id) + ">, you have taken too long to complete this process. Please feel free to make a new message and restart the process at any time."
		discord_message_id = discord_user_id
		reply_data = {'content': reply_text, 'message_reference': {'message_id': discord_message_id}}
		requests.post(baseURL, headers=headers, data=json.dumps(reply_data))
		requests.delete(deleteMessageURL.format(TOKENS["pairing_channel"], discord_message_id), headers=headers)
		requests.post(request_url + "/remove-account-pairing-request/", data={"discord_user_id": discord_user_id})

# Check Reddit for unread replies
reddit_messages = get_reddit_messages(reddit)
for reddit_message in reddit_messages:
	try:
		reddit_message_id = reddit_message.parent_id.split("_")[-1]
	except:
		print("Unable to parse reddit message. Skipping...")
		continue
	for discord_user_id, data in pending_requests.items():
		if not reddit_message_id == data['reddit_message_id']:
			continue
		requests.post(request_url + "/add-username-pairing/", data={'platform1': 'discord', 'username1': discord_user_id, 'platform2': 'reddit', 'username2': data['reddit_username']}).json()
		try:
			reddit_message.reply("Thank you for confirming your identity. Your discord account is now linked to your reddit account.")
		except:
			pass
		requests.put(roleURL.format(discord_user_id, TOKENS['role_id']), headers=headers)
		message_data = {'content': "<@"+discord_user_id+"> -> "+data['reddit_username']}
		requests.post(logBaseURL, headers=headers, data=json.dumps(message_data))
		requests.post(request_url + "/remove-account-pairing-request/", data={"discord_user_id": discord_user_id})

# Dump the relevant databases
json_helper.dump(pending_requests, "Discord/pending_requests.json")
