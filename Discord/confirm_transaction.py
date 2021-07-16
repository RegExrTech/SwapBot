import time
import json_helper
import requests
import re
import json
import praw

time_limit_minutes = 30
time_limit = time_limit_minutes * 60 # Seconds

bot_username = "Swap Bot#0749"
request_url = "http://0.0.0.0:8000"

TOKENS = json_helper.get_db("tokens.json")
confirmation_channel = TOKENS["confirmation_channel"]
server_id = TOKENS["server_id"]

baseURL = "https://discordapp.com/api/channels/{}/messages".format(TOKENS["confirmation_channel"])
bst_channel_url = "https://discordapp.com/api/channels/{}/messages/{}"
headers = {"Authorization":"Bot {}".format(TOKENS["token"]),
	"User-Agent":"SwapBot (https://www.regexr.tech, v0.1)",
	"Content-Type":"application/json"}


def get_mentioned_users(text, invalids):
	pattern = re.compile("<@!([0-9]{18})>")
	found = re.findall(pattern, text)
	return list(set([x for x in found if x not in invalids]))

def get_mentioned_roles(text):
	pattern = re.compile("<@&([0-9]{18})>")
	return list(set(re.findall(pattern, text)))

def get_mentioned_posts(text, invalids):
	pattern = re.compile("([0-9]{18})")
	found = re.findall(pattern, text)
	return list(set([x for x in found if x not in invalids]))

def get_correct_channel_id(post_id):
	bst_channel_ids = TOKENS['bst_channels']
	for bst_channel_id in bst_channel_ids:
		r = requests.get(bst_channel_url.format(bst_channel_id, post_id), headers = headers)
		if r.ok:
			return bst_channel_id, r.json()
	return None, {}

def reply(message, reply_id):
	message_data = {'content': message, 'message_reference': {'message_id': reply_id}}
	requests.post(baseURL, headers=headers, data=json.dumps(message_data))

r = requests.get(baseURL, headers = headers)
messages = r.json()

confirmation_invocations = []
confirmation_replies = []
messages_to_ignore = []
# Check Discord for messages
for message in messages:
	author1_id = message['author']['id']
	bot_user_id = TOKENS["bot_id"]
	if "referenced_message" in message and bot_user_id != author1_id and message['referenced_message']['author']['id'] == bot_user_id:
		confirmation_replies.append(message)
	elif bot_user_id != author1_id and "referenced_message" not in message:
		confirmation_invocations.append(message)
	elif "referenced_message" in message and bot_user_id == author1_id:
		messages_to_ignore.append(message["referenced_message"])

for message in messages_to_ignore:
	confirmation_invocations = [x for x in confirmation_invocations if x['id'] != message['id']]
	confirmation_replies = [x for x in confirmation_replies if x['id'] != message['id']]

for message in confirmation_invocations:
	body = message['content']
	author1_id = message['author']['id']
	bot_user_id = TOKENS["bot_id"]
	confirmation_message_id = message['id']
	invalids = [bot_user_id, author1_id]
	# If the message is from the bot, skip
	if bot_user_id == author1_id:
		continue

	mentioned_users = get_mentioned_users(body, invalids)
	if not mentioned_users:
		reply("You did not mention any users in your message. Please try again.", confirmation_message_id)
		continue

	mentioned_roles = get_mentioned_roles(body)

	mentioned_posts = get_mentioned_posts(body, mentioned_users+mentioned_roles+invalids)
	if not mentioned_posts:
		reply("You did not mention any posts in your message. Please try again.", confirmation_message_id)
		continue

	author2_id = mentioned_users[0]
	original_post_id = mentioned_posts[0]
	channel_id, original_post_data = get_correct_channel_id(original_post_id)
	if not channel_id:
		reply("I could not find the message you are referring to in any of the BST channels. Please try again with a correct message ID.", confirmation_message_id)
		continue

	desired_author_id = original_post_data['author']['id']
	if desired_author_id not in [author1_id, author2_id]:
		reply("Neither you nor the person you tagged are the OP of the message you referenced.", confirmation_message_id)
		continue

	full_original_post_url = "https://discord.com/channels/" + server_id + "/" + channel_id + "/" + original_post_id
	message_data = {'content': "<@"+author2_id+">, if you have **COMPLETED** a transaction with <@"+author1_id+"> from the following post, please **REPLY** to this message indicating as such:\n\n" + full_original_post_url + "\n\nIf you did NOT complete such a transaction, please DO NOT REPLY to this message and instead inform the Officers right away.", 'message_reference': {'message_id': confirmation_message_id}}
	requests.post(baseURL, headers=headers, data=json.dumps(message_data))

for message in confirmation_replies:
	print('ere')
	author1_id = message['author']['id']
	bot_reply_id = message['referenced_message']['id']
	bot_message = requests.get(baseURL+"/"+bot_reply_id, headers = headers).json()
	author2_message = bot_message['referenced_message']
	author2_id = author2_message['author']['id']
	if author1_id not in [x['id'] for x in author2_message['mentions']]:
		reply("You replied to a message that did not tag you. Please do not do that.", message['id'])
		continue
	if author1_id == author2_id:
		reply("Sorry, but you cannot confirm a transaction with yourself.", message['id'])
		continue

	# Check that the confirmation is NOT a duplicate
	# Save data to database
	# Update flair if appropriate
	# Update ranks if appropriate
	reply("This transaction has been recoreded for <@!" + author2_id + "> and <@!" + author1_id + ">.", message['id'])
