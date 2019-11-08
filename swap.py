import requests
import re
import json
import praw
import time
import datetime
import argparse

debug = False
silent = False

# IDK, I needed this according to stack overflow.
def ascii_encode_dict(data):
        ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
        return dict(map(ascii_encode, pair) for pair in data.items())

# Function to load the swap DB into memory
def get_swap_data(fname):
        with open(fname) as json_data: # open the funko-shop's data
                funko_store_data = json.load(json_data, object_hook=ascii_encode_dict)
        return funko_store_data

request_url = "http://192.168.1.210:8000"

parser = argparse.ArgumentParser()
parser.add_argument('config_file_name', metavar='C', type=str)
args = parser.parse_args()
config_fname = 'config/' + args.config_file_name

f = open(config_fname, "r")
info = f.read().splitlines()
f.close()

subreddit_name = info[0].split(":")[1]
if subreddit_name in ['digitalcodesell', 'uvtrade']:
	database_name = 'digitalcodeexchange'
else:
	database_name = subreddit_name
client_id = info[1].split(":")[1]
client_secret = info[2].split(":")[1]
bot_username = info[3].split(":")[1]
bot_password = info[4].split(":")[1]
if info[5].split(":")[1]:
	flair_word = " " + info[5].split(":")[1]
else:
	flair_word = " Swaps"
if info[6].split(":")[1]:
	mod_flair_word = info[6].split(":")[1] + " "
else:
	mod_flair_word = ""
if info[7].split(":")[1]:
	flair_templates = get_swap_data('templates/'+subreddit_name+'.json')
else:
	flair_templates = False
if info[8].split(":")[1]:
	confirmation_text = info[8].split(":")[1]
else:
	confirmation_text = "Added"
if info[9].split(":")[1]:
	flair_threshold = int(info[9].split(":")[1])
else:
	flair_threshold = 0
if info[10].split(":")[1]:
	mod_flair_template = info[10].split(":")[1]
else:
	mod_flair_template = ""
if info[11].split(":")[1]:
        titles = get_swap_data('titles/'+subreddit_name+'.json')
else:
        titles = False

check_time = datetime.datetime.utcnow().time()

# Checks if the time at script start up is between two desired times
def is_time_between(begin_time, end_time):
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

# Method for giving credit to users when they do a trade.
# Returns True if credit was given, False otherwise
def update_database(author1, author2, post_id, comment_id):
	author1 = str(author1).lower()  # Create strings of the user names for keys and values
	author2 = str(author2).lower()

	# Default generic value for swaps
	return_data = requests.post(request_url + "/check-comment/", {'sub_name': database_name, 'author1': author1, 'author2': author2, 'post_id': post_id, 'comment_id': comment_id, 'real_sub_name': subreddit_name}).json()
	is_duplicate = return_data['is_duplicate'] == 'True'
	flair_count_1 = return_data['flair_count_1']
	flair_count_2 = return_data['flair_count_2']
	return not is_duplicate, flair_count_1, flair_count_2

def get_flair_template(templates, count):
	if not templates:
		return ""
	keys = [int(x) for x in templates.keys()]
	keys.sort()
	template = ""
	for key in keys:
		if key > count:
			break
		template = templates[str(key)]
	return template

def update_flair(author1, author2, author1_count, author2_count, sub):
	mods = [str(x).lower() for x in sub.moderator()]
	author1 = str(author1).lower()  # Create strings of the user names for keys and values
	author2 = str(author2).lower()

	# Loop over each author and change their flair
	for pair in [(author1, author1_count), (author2, author2_count)]:
		author = pair[0]
		swap_count = str(pair[1])
		print("attempting to assign flair for " + author)
		if int(swap_count) < flair_threshold and not author == 'totallynotregexr':
			print(author + " has a swap count of " + swap_count + " which is below the thresold of " + str(flair_threshold))
			continue
		template = get_flair_template(flair_templates, int(swap_count))
		title = get_flair_template(titles, int(swap_count))
		if not debug:
			flair_text = swap_count + flair_word
			if author in mods:
				template = mod_flair_template
				flair_text = mod_flair_word + flair_text
			if title:
				flair_text += " | " + title

			if template:
				sub.flair.set(author, flair_text, flair_template_id=template)
			else:
				sub.flair.set(author, flair_text, swap_count)
		else:
			print("Assigning flair " + swap_count + " to user " + author + " with template_id: " + template)
			print("==========")

def set_active_comments_and_messages(reddit, comments, messages):
        # Get comments from username mentions
	ids = []
	to_mark_as_read = []
	try:
		for message in reddit.inbox.unread():
			to_mark_as_read.append(message)
        	        if message.was_comment and message.subject == "username mention" and (not str(message.author).lower() == "automoderator"):
                	        try:
					ids.append(message.id)
	                        except:  # if this fails, the user deleted their account or comment so skip it
        	                        pass
                	elif not message.was_comment:
                        	messages.append(message)
	except Exception as e:
		print(e)
		print("Failed to get next message from unreads. Ignoring all unread messages and will try again next time.")

	ids = requests.post(request_url + "/get-comments/", {'sub_name': subreddit_name, 'active': 'True', 'ids': ",".join(ids)}).json()['ids']
        ids = list(set(ids))  # Dedupe just in case we get duplicates from the two sources
        for comment_id in ids:
                try:
                        comments.append(reddit.comment(comment_id))
                except:  # If we fail, the user deleted their comment or account, so skip
                        pass

	if not debug:
		for message in to_mark_as_read:
			try:
				message.mark_read()
			except:
				print("Unable to mark message as read. Leaving it as is.")


def set_archived_comments(reddit, comments):
	ids = ",".join([comment.id for comment in comments])
	all_ids = requests.post(request_url + "/get-comments/", {'sub_name': subreddit_name, 'active': 'False', 'ids': ids}).json()['ids']
	for id in all_ids:
		if id not in ids: # if this was not already passed in
			comments.append(reddit.comment(id))

def handle_comment(comment, bot_username, sub):
	# If this is someone responding to a tag by tagging the bot, we want to ignore them.
	if isinstance(comment.parent(), praw.models.Comment) and bot_username in comment.parent().body and 'automod' not in str(comment.parent().author).lower():
		requests.post(request_url + "/remove-comment/", {'sub_name': subreddit_name, 'comment_id': comment.id})
		return True
        author1 = comment.author  # Author of the top level comment
        comment_word_list = [x.encode('utf-8').strip() for x in comment.body.lower().replace(",", '').replace("\n", " ").replace("\r", " ").replace(".", '').replace("?", '').replace("!", '').replace("[", '').replace("]", " ").replace("(", '').replace(")", " ").replace("*", '').replace("\\", "").split(" ")]  # all words in the top level comment
	if debug:
		print(" ".join(comment_word_list))
        desired_author2_string = get_desired_author2_name(comment_word_list, bot_username, str(author1))
        if not desired_author2_string:
                handle_no_author2(comment_word_list, comment)
		requests.post(request_url + "/remove-comment/", {'sub_name': subreddit_name, 'comment_id': comment.id})
                return True
        correct_reply = find_correct_reply(comment, author1, desired_author2_string)
        if correct_reply:
                author2 = correct_reply.author
		if debug:
			print("Author1: " + str(author1))
			print("Author2: " + str(author2))
                if correct_reply.is_submitter or comment.is_submitter:  # make sure at least one of them is the OP for the post
                        parent_post = comment
                        while parent_post.__class__.__name__ == "Comment":  # Ensures we actually get the id of the parent POST and not just a parent comment
                                parent_post = parent_post.parent()
                        credit_given, author1_count, author2_count = update_database(author1, author2, parent_post.id, comment.id)
                        if credit_given:
                                inform_giving_credit(correct_reply)
                                update_flair(author1, author2, author1_count, author2_count, sub)
                        else:
                                inform_credit_already_given(correct_reply)
				requests.post(request_url + "/remove-comment/", {'sub_name': subreddit_name, 'comment_id': comment.id})
		return True
        else:  # If we found no correct looking comments, let's come back to it later
		if debug:
			print("No correct looking replies were found")
		return False

def get_desired_author2_name(comment_word_list, bot_username, author_username_string):
	for word in comment_word_list:  # We try to find the person being tagged in the top level comment
		if "u/" in word and bot_username.lower() not in word:
			desired_author2_string = word
			if desired_author2_string[0] == "/":  # Sometimes people like to add a / to the u/username
				desired_author2_string = desired_author2_string[1:]
			if not desired_author2_string[2:] == author_username_string.lower():
 				return desired_author2_string
	return ""

def handle_no_author2(comment_word_list, comment):
	print("\n\n" + str(time.time()) + "\n" + "Unable to find a username in " + str(comment_word_list) + " for post " + comment.parent().id)
	try:
		if not debug:
			if not silent:
				comment.reply("You did not tag anyone other than this bot in your comment. Please post a new top level comment tagging this bot and the person you traded with to get credit for the trade.")
			else:
				print("You did not tag anyone other than this bot in your comment. Please post a new top level comment tagging this bot and the person you traded with to get credit for the trade." + "\n==========")
		else:
			print("You did not tag anyone other than this bot in your comment. Please post a new top level comment tagging this bot and the person you traded with to get credit for the trade." + "\n==========")
	except Exception as e:  # Comment was probably deleted
		print("\n\n" + str(time.time()) + "\n" + str(e))

def find_correct_reply(comment, author1, desired_author2_string):
	replies = comment.replies
	replies.replace_more(limit=None)
	for reply in replies.list():
		potential_author2_string = "u/"+str(reply.author).lower()
		if not potential_author2_string == desired_author2_string:
			continue
                if str(author1).lower() == potential_author2_string:  # They can't get credit for swapping with themselves
                        continue
                return reply
	return None

def inform_comment_archived(comment):
	try:
		if not debug:
			word_list = [x.encode('utf-8').strip() for x in comment.body.lower().replace(",", '').replace("\n", " ").replace("\r", " ").replace(".", '').replace("?", '').replace("!", '').replace("[", '').replace("]", " ").replace("(", '').replace(")", " ").replace("*", '').replace("\\", "").split(" ")]
			author2 = get_desired_author2_name(word_list, bot_username, str(comment.author))
			if not silent:
				comment.reply(author2 + ", please reply to the comment above this to confirm with your trade partner.\n\nThis comment has been around for more than 3 days without a response. The bot will still track this comment but it will only check it once a day. This means that if your trade partner replies to your comment, it will take up to 24 hours before your comment is confirmed. Please wait that long before messaging the mods for help. If you are getting this message but your partner has already confirmed, please message the mods for assistance.")
			else:
				print("This comment has been around for more than 3 days without a response. The bot will still track this comment but it will only check it once a day. This means that if your trade partner replies to your comment, it will take up to 24 hours before your comment is confirmed. Please wait that long before messaging the mods for help. If you are getting this message but your partner has already confirmed, please message the mods for assistance.")
			requests.post(request_url + "/archive-comment/", {'sub_name': subreddit_name, 'comment_id': comment.id})
		else:
			print("This comment has been around for more than 3 days without a response. The bot will still track this comment but it will only check it once a day. This means that if your trade partner replies to your comment, it will take up to 24 hours before your comment is confirmed. Please wait that long before messaging the mods for help. If you are getting this message but your partner has already confirmed, please message the mods for assistance.")
	except Exception as e:
		print("\n\n" + str(time.time()) + "\n" + str(e))  # comment was probably deleted

def inform_comment_deleted(comment):
	try:
		if not debug:
			if not silent:
				comment.reply("This comment has been around for more than a month and will no longer be tracked. If you wish to attempt to get trade credit for this swap again, please make a new comment and tag both this bot and your trade partner.")
			else:
				print("This comment has been around for more than a month and will no longer be tracked. If you wish to attempt to get trade credit for this swap again, please make a new comment and tag both this bot and your trade partner.")
		else:
			print("This comment has been around for more than a month and will no longer be tracked. If you wish to attempt to get trade credit for this swap again, please make a new comment and tag both this bot and your trade partner.")
	except Exception as e:
		print("\n\n" + str(time.time()) + "\n" + str(e))  # comment was probably deleted

def inform_giving_credit(correct_reply):
	try:
		if not debug:
			if not silent:
				correct_reply.reply(confirmation_text)
			else:
				print(confirmation_text + "\n==========")
		else:
			print(confirmation_text + "\n==========")
	except Exception as e:  # Comment was porobably deleted
		print("\n\n" + str(time.time()) + "\n" + str(e))

def inform_credit_already_given(correct_reply):
	try:
		if not debug:
			if not silent:
				correct_reply.reply("You already got credit for this trade. Please contact the moderators if you think this is an error.")
			else:
				print("You already got credit for this trade. Please contact the moderators if you think this is an error." + "\n==========")
		else:
			print("You already got credit for this trade. Please contact the moderators if you think this is an error." + "\n==========")
	except Exception as e:  # Comment was probably deleted
		print("\n\n" + str(time.time()) + "\n" + str(e))

def main():
	reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent='UserAgent', username=bot_username, password=bot_password)
	sub = reddit.subreddit(subreddit_name)

	comments = []  # Stores comments from both sources of Ids
        messages = []  # Want to catch everything else for replying
	set_active_comments_and_messages(reddit, comments, messages)

	# Process comments
	if debug:
		print("Looking through active comments...")
	for comment in comments:
		try:
			comment.refresh()  # Don't know why this is required but it doesnt work without it so dont touch it
		except: # if we can't refresh a comment, archive it so we don't waste time on it.
			print("Could not 'refresh' comment: " + str(comment))
			requests.post(request_url + "/archive-comment/", {'sub_name': subreddit_name, 'comment_id': comment.id})
			continue
		handeled = handle_comment(comment, bot_username, sub)
		time_made = comment.created
		if time.time() - time_made > 3 * 24 * 60 * 60:  # if this comment is more than three days old
			if not handeled:
				inform_comment_archived(comment)

	# If it is between 00:00 and 00:09 UTC, check the archived comments
	if is_time_between(datetime.time(2,0), datetime.time(2,9)) or debug:
#	if True:
		print("Looking through archived comments...")
		comments = []
		set_archived_comments(reddit, comments)
		for comment in comments:
	                try:
        	                comment.refresh()  # Don't know why this is required but it doesnt work without it so dont touch it
                	except:
                        	print("Could not 'refresh' comment: " + str(comment))
	                        continue
			time_made = comment.created
			if time.time() - time_made > 30 * 24 * 60 * 60:  # if this comment is more than thirty days old
				inform_comment_deleted(comment)
				requests.post(request_url + "/remove-comment/", {'sub_name': subreddit_name, 'comment_id': comment.id})
			else:
				handle_comment(comment, bot_username, sub)
			time.sleep(.5)

	# This is for if anyone sends us a message requesting swap data
	for message in messages:
		text = (message.body + " " +  message.subject).replace("\n", " ").replace("\r", " ").split(" ")  # get each unique word
		username = ""  # This will hold the username in question
		for word in text:
			if '/u/' in word.lower():  # Same as above but if they start with a leading /u/ instead of u/
				username = word.lower()[3:]
				break
			if 'u/' in word.lower():  # if we have a username
				username = word.lower()[2:]  # Save the username and break early
				break
		if not username:  # If we didn't find a username, let them know and continue
			if not debug:
				try:
					if not silent:
						message.reply("Hi there,\n\nYou did not specify a username to check. Please ensure that you have a user name, in the body of the message you just sent me. Please feel free to try again. Thanks!")
					else:
						print("Hi there,\n\nYou did not specify a username to check. Please ensure that you have a user name in the body of the message you just sent me. Please feel free to try again. Thanks!" + "\n==========")
				except Exception as e:
					print("Could not reply to message with error...")
					print("    " + str(e))
			else:
				print("Hi there,\n\nYou did not specify a username to check. Please ensure that you have a user name in the body of the message you just sent me. Please feel free to try again. Thanks!" + "\n==========")
			continue
		final_text = ""
		trades = requests.post(request_url + "/get-summary/", {'sub_name': database_name, 'username': username}).json()['data']
		if not trades:  # if that user has not done any trades, we have no info for them.
			if not debug:
				try:
					if not silent:
						message.reply("Hello,\n\nu/" + username + " has not had any swaps yet.")
					else:
						print("Hello,\n\nu/" + username + " has not had any swaps yet." + "\n==========")
				except Exception as e:
					print("Could not reply to message with error...")
					print("    " + str(e))
			else:
				print("Hello,\n\nu/" + username + " has not had any swaps yet." + "\n==========")
			continue

		legacy_count = 0  # Use this to track the number of legacy swaps someone has
		for trade in trades[::-1]:
			if trade == "LEGACY TRADE":
				legacy_count += 1
			else:
				final_text += "*  u/" + trade + "\n\n"

		if legacy_count > 0:
			final_text = "* " + str(legacy_count) + " Legacy Trades (trade done before this bot was created)\n\n" + final_text

		if len(trades) == 0:
			if not debug:
				try:
					if not silent:
						message.reply("Hello,\n\nu/" + username + " has not had any swaps yet.")
					else:
						print("Hello,\n\nu/" + username + " has not had any swaps yet." + "\n==========")
				except Exception as e:
					print("Could not reply to message with error...")
					print("    " + str(e))
			else:
				print("Hello,\n\nu/" + username + " has not had any swaps yet." + "\n==========")
		else:
			if not debug:
				try:
					if len(final_text) > 10000:
						final_text = final_text[:9800] + "\nTruncated..."
					if not silent:
						message.reply("Hello,\n\nu/" + username + " has had the following " + str(len(trades)) + " swaps:\n\n" + final_text)
					else:
						print("Hello,\n\nu/" + username + " has had the following " + str(len(trades)) + " swaps:\n\n" + final_text + "\n==========")
				except Exception as e:
					print("Could not reply to message with error...")
					print("    " + str(e))
			else:
				print("Hello,\n\nu/" + username + " has had the following " + str(len(trades)) + " swaps:\n\n" + final_text + "\n==========")

main()
