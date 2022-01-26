import datetime
import time
import json_helper
import requests
import re
import json
import praw
import argparse
import sys
sys.path.insert(0, ".")
sys.path.insert(0, "Discord")
from assign_role import assign_role
from config import Config
import swap
import time

parser = argparse.ArgumentParser()
parser.add_argument('sub_name', metavar='C', type=str)
args = parser.parse_args()
sub_config = Config(args.sub_name.lower())


bot_username = "Swap Bot#0749"
request_url = "http://0.0.0.0:8000"

TOKENS = json_helper.get_db("Discord/config/" + args.sub_name.lower() + ".json")
confirmation_channel = TOKENS["confirmation_channel"]
server_id = TOKENS["server_id"]

bareUrl = "https://discordapp.com/api/channels/{}/messages"
baseUrl = bareUrl.format(TOKENS["confirmation_channel"])
feedbackUrl = bareUrl.format(TOKENS["feedback_check_channel"])
bst_channel_url = "https://discordapp.com/api/channels/{}/messages/{}"
headers = {"Authorization":"Bot {}".format(TOKENS["token"]),
	"User-Agent":"SwapBot (https://www.regexr.tech, v0.1)",
	"Content-Type":"application/json"}

debug = False
silent = False
PLATFORM = "discord"
kofi_text = "\n\n---\nBuy the developer a coffee: <https://kofi.regexr.tech>"

POST = "post"
PUT = "put"
GET = "get"
PATCH = "patch"

def send_request(type, url, headers, data="{}", should_retry=True, is_embed=False):
	valid_status_codes = [200, 204]

	if type == POST:
		r = requests.post(url, headers=headers, data=data)
	elif type == PUT:
		r = requests.put(url, headers=headers)
	elif type == GET:
		r = requests.get(url, headers=headers)
	elif type == PATCH:
		r = requests.patch(url, headers=headers, data=data)
	else:
		return

	if r.status_code not in valid_status_codes:
		if (is_embed and len(data) > 6000) or (not is_embed and len(data) > 1993):
			print("Discord data too big: \n" + data)
			return r
		status_data = r.json()
		if 'retry_after' in status_data and should_retry:
			time.sleep((status_data['retry_after']/1000.0) + 0.1) # Add some buffer to the sleep
			return send_request(type, url, headers, data, False, is_embed)
		else:
			print("Discord Failure - status: " + str(r.status_code) + " - text: " + r.text + "\nData: " + str(data))
	return r

def get_embedded_messaged_template(content="", title="", url="", description=""):
	data = {
		"content": content,
		"embed": {
			"title": title,
			"author": {
				"name": "RegExrBot",
				"url": "https://www.regexr.tech/",
				"icon_url": "https://cdn.discordapp.com/avatars/333321993036365826/085c4e12517e7e6770bb7ee788706aa6.png?size=256"
			},
			"color": 8564590,
			"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M").replace(" ", "T") + ":00.000Z",
			"thumbnail": {},
			"image": {},
			"description": description,
			"fields": []
		}
	}
	if url:
		data['embed']['url'] = url
	return data

def create_embedded_feedback_check_reply(reply_id, user_id, username, confirmations):
	def _get_embed(content, title, image_url=""):
		data = get_embedded_messaged_template(content=content, title=title, url=image_url)
		data['embed']['fields'].append({
			"name": "Detailed Feedback List",
			"value": ""
		})
		return data

	def _get_next_embed():
		title = ""
		content = "continued..."
		return _get_embed(content, title)


	title = username + " has " + str(len(transactions)) + " confirmed transactions"
	content = kofi_text[6:]
	data = _get_embed(content, title)
	data['message_reference'] = {'message_id': reply_id}
	replies = []
	string_length = len(json.dumps(data))
	first_reply_in_field = True
	for confirmation in confirmations:
		if "LEGACY TRADE" in confirmation:
			next_item_string = confirmation
		else:
			partner = confirmation.split(" - ")[0]
			url = confirmation.split(" - ")[1]
			next_item_string = "[" + partner + "](" + url + ")"
		if first_reply_in_field:
			first_reply_in_field = False
		else:
			next_item_string = " | " + next_item_string
		if string_length + len(next_item_string) < 6000:
			string_length += len(next_item_string)
			if len(data['embed']['fields'][-1]['value']) + len(next_item_string) > 1024:
				first_reply_in_field = True
				data['embed']['fields'].append({"name": "-", "value": ""})
				string_length = len(json.dumps(data)) + len(next_item_string)
				if string_length >= 6000:
					data['embed']['fields'] = data['embed']['fields'][:-1]
					replies.append(json.dumps(data))
					data = _get_next_embed()
					string_length = len(json.dumps(data)) + len(next_item_string)
		else:
			replies.append(json.dumps(data))
			first_reply_in_field = True
			data = _get_next_embed()
			string_length = len(json.dumps(data)) + len(next_item_string)
		if first_reply_in_field:
			next_item_string = next_item_string[3:]
			first_reply_in_field = False
		data['embed']['fields'][-1]['value'] += next_item_string

	if data['embed']['fields'][-1]['value']:
		replies.append(json.dumps(data))

	return replies

def get_mentioned_users(message, invalids):
	return list(set([x['id'] for x in message['mentions'] if x['id'] not in invalids]))

def get_mentioned_usernames(message, invalids):
	invalids = [x.lower() for x in invalids]
	return list(set([x['username'] for x in message['mentions'] if x['username'].lower() not in invalids]))

def get_mentioned_roles(message):
	return list(set(x['id'] for x in message['mention_roles']))

def get_mentioned_posts(text, invalids):
	pattern = re.compile("([0-9]{18})")
	found = re.findall(pattern, text)
	return list(set([x for x in found if x not in invalids]))

def get_url(text):
	pattern = re.compile("(https://.*)")
	found = re.findall(pattern, text)
	if not found:
		return None
	return found[0]

def get_correct_channel_id(post_id):
	bst_channel_ids = TOKENS['bst_channels']
	for bst_channel_id in bst_channel_ids:
		r = send_request(GET, bst_channel_url.format(bst_channel_id, post_id), headers)
		if r.ok:
			return bst_channel_id, r.json()
	return None, {}

def reply(message, reply_id, url):
	message += kofi_text
	message_data = {'content': message, 'message_reference': {'message_id': reply_id}}
	if not debug:
		send_request(POST, url, headers, json.dumps(message_data))
	else:
		print("Would have sent message: " + message)

def update_database(author1, author2, listing_url):
	return_data = requests.post(request_url + "/check-comment/", {'sub_name': sub_config.database_name, 'author1': author1, 'author2': author2, 'post_id': listing_url, 'comment_id': "", 'real_sub_name': sub_config.subreddit_name, 'platform': PLATFORM}).json()
	is_duplicate = return_data['is_duplicate'] == 'True'
	return is_duplicate

messages = send_request(GET, baseUrl, headers).json()

confirmation_invocations = []
confirmation_replies = []
messages_to_ignore = []
# Check Discord for messages
for message in messages:
	author1_id = message['author']['id']
	bot_user_id = TOKENS["bot_id"]
	if "referenced_message" in message and message["referenced_message"] is not None and bot_user_id != author1_id and message['referenced_message']['author']['id'] == bot_user_id:
		confirmation_replies.append(message)
	elif bot_user_id != author1_id and "referenced_message" not in message:
		confirmation_invocations.append(message)
	elif "referenced_message" in message and bot_user_id == author1_id:
		messages_to_ignore.append(message["referenced_message"])

for message in messages_to_ignore:
	if not message:
		continue
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

	mentioned_users = get_mentioned_users(message, invalids)
	if not mentioned_users:
		reply("You did not mention any users in your message. Please try again.", confirmation_message_id, baseUrl)
		continue

	mentioned_roles = get_mentioned_roles(message)

	mentioned_posts = get_mentioned_posts(body, mentioned_users+mentioned_roles+invalids)
	if not mentioned_posts:
		reply("You did not mention any posts in your message. Please try again.", confirmation_message_id, baseUrl)
		continue

	author2_id = mentioned_users[0]
	original_post_id = mentioned_posts[0]
	channel_id, original_post_data = get_correct_channel_id(original_post_id)
	if not channel_id:
		reply("I could not find the message you are referring to in any of the BST channels. Please try again with a correct message ID.", confirmation_message_id, baseUrl)
		continue

	desired_author_id = original_post_data['author']['id']
	if desired_author_id not in [author1_id, author2_id]:
		reply("Neither you nor the person you tagged are the OP of the message you referenced.", confirmation_message_id, baseUrl)
		continue

	full_original_post_url = "https://www.discord.com/channels/" + server_id + "/" + channel_id + "/" + original_post_id
	reply_message = "<@"+author2_id+">, if you have **COMPLETED** a transaction with <@"+author1_id+"> from the following post, please **REPLY TO THIS MESSAGE** indicating as such:\n\n" + full_original_post_url + "\n\nIf you did NOT complete such a transaction, please DO NOT REPLY to this message and instead send a DM to <@698942482716688445> right away."
	reply(reply_message, confirmation_message_id, baseUrl)

paired_usernames = requests.get(request_url + "/get-paired-usernames/").json()

for message in confirmation_replies:
	author1_id = message['author']['id']
	bot_reply_id = message['referenced_message']['id']
	bot_message = send_request(GET, baseUrl+"/"+bot_reply_id, headers).json()
	author2_message = bot_message['referenced_message']
	author2_id = author2_message['author']['id']
	if author1_id not in [x['id'] for x in author2_message['mentions']]:
		reply("You replied to a message that did not tag you. Please do not do that.", message['id'], baseUrl)
		continue
	if author1_id == author2_id:
		reply("Sorry, but you cannot confirm a transaction with yourself.", message['id'], baseUrl)
		continue

	full_original_post_url = get_url(bot_message['content'])
	if not full_original_post_url:
		reply("Please only reply to messages that I tag you in. Thank you!", message['id'], baseUrl)
		continue

	is_duplicate = update_database(author1_id, author2_id, full_original_post_url)
	if is_duplicate:
		reply("Sorry, but you already got credit for this transaction.", message['id'], baseUrl)
		continue

	for discord_user_id in [author1_id, author2_id]:
		for sub_name in [sub_config.subreddit_name] + sub_config.gives_flair_to:
			if sub_name not in sub_config.sister_subs:
				sister_sub_config, sister_reddit, sister_sub = swap.create_reddit_and_sub(sub_name)
				sub_config.sister_subs[sub_name] = {'reddit': sister_reddit, 'sub': sister_sub, 'config': sister_sub_config}
			current_sub_config = sub_config.sister_subs[sub_name]['config']
			if not current_sub_config.discord_config:
				continue
			swap_count = str(swap.get_swap_count(discord_user_id, [sub_name] + current_sub_config.gets_flair_from, PLATFORM))
			discord_role_id = swap.get_discord_role(current_sub_config.discord_roles, int(swap_count))
			assign_role(current_sub_config.discord_config.server_id, discord_user_id, discord_role_id)
		if discord_user_id in paired_usernames['discord']:
			tmp_sub_config, tmp_reddit, tmp_sub = swap.create_reddit_and_sub(sub_config.subreddit_name)
			if 'reddit' in paired_usernames['discord'][discord_user_id]:
				reddit_username_string = paired_usernames['discord'][discord_user_id]['reddit']
				reddit_user = tmp_reddit.redditor(reddit_username_string)
				swap.update_flair(reddit_user, None, sub_config)

	reply("This transaction has been recorded for <@!" + author2_id + "> and <@!" + author1_id + ">.", message['id'], baseUrl)


# REPLY TO REQUESTS FOR FEEDBACK

messages = send_request(GET, feedbackUrl, headers).json()
invocations = []
messages_to_ignore = []
for message in messages:
	author_id = message['author']['id']
	bot_user_id = TOKENS["bot_id"]
	if bot_user_id != author_id and "referenced_message" not in message:
		invocations.append(message)
	elif "referenced_message" in message and bot_user_id == author_id:
		messages_to_ignore.append(message["referenced_message"])

for message in messages_to_ignore:
	if not message:
		continue
	invocations = [x for x in invocations if x['id'] != message['id']]

for message in invocations:
	user_to_check_list = get_mentioned_users(message, [])
	if not user_to_check_list:
		continue
	user_to_check = user_to_check_list[0]
	username = get_mentioned_usernames(message, [])[0]
	transactions = requests.post(request_url + "/get-summary/", {'sub_name': sub_config.subreddit_name, 'current_platform': PLATFORM, 'username': user_to_check}).json()['data']
	if not transactions:
		reply("<@!" + user_to_check + "> has not confirmed any transactions yet.", message['id'], feedbackUrl)
		continue
	formatted_replies = create_embedded_feedback_check_reply(message['id'], author_id, username, transactions)
	for formatted_reply in formatted_replies:
		send_request(POST, feedbackUrl, headers, data=formatted_reply, should_retry=True, is_embed=True)

