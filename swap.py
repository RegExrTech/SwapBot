import sys
sys.path.insert(0, '.')
import config
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

request_url = "http://192.168.0.155:8000"

parser = argparse.ArgumentParser()
parser.add_argument('sub_name', metavar='C', type=str)
args = parser.parse_args()
sub_config = config.Config(args.sub_name.lower())

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
	return_data = requests.post(request_url + "/check-comment/", {'sub_name': sub_config.database_name, 'author1': author1, 'author2': author2, 'post_id': post_id, 'comment_id': comment_id, 'real_sub_name': sub_config.subreddit_name}).json()
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
	"""returns list of tuples of author name and (str)swap count if flair was NOT updated."""
	author1 = str(author1).lower()  # Create strings of the user names for keys and values
	author2 = str(author2).lower()
	non_updated_users = []
	# Loop over each author and change their flair
	for pair in [(author1, author1_count), (author2, author2_count)]:
		update_single_user_flair(sub, sub_config, pair[0], str(pair[1]), non_updated_users, debug)
	return non_updated_users

def update_single_user_flair(sub, sub_config, author, swap_count, non_updated_users, debug=False):
	print("attempting to assign flair for " + author)
	mods = [str(x).lower() for x in sub.moderator()]
	if int(swap_count) < sub_config.flair_threshold and not author == 'totallynotregexr':
		non_updated_users.append((author, swap_count))
		return
	template = get_flair_template(sub_config.flair_templates, int(swap_count))
	title = get_flair_template(sub_config.titles, int(swap_count))
	if not debug:
		flair_text = swap_count + sub_config.flair_word
		if author in mods:
			template = sub_config.mod_flair_template
			flair_text = sub_config.mod_flair_word + flair_text
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

	ids = requests.post(request_url + "/get-comments/", {'sub_name': sub_config.subreddit_name, 'active': 'True', 'ids': ",".join(ids)}).json()['ids']
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
			except Exception as e:
				print(e)
				print("Unable to mark message as read. Leaving it as is.")


def set_archived_comments(reddit, comments):
	ids = ",".join([comment.id for comment in comments])
	all_ids = requests.post(request_url + "/get-comments/", {'sub_name': sub_config.subreddit_name, 'active': 'False', 'ids': ids}).json()['ids']
	for id in all_ids:
		if id not in ids: # if this was not already passed in
			comments.append(reddit.comment(id))

def handle_comment(comment, bot_username, sub):
	# If this is someone responding to a tag by tagging the bot, we want to ignore them.
	if isinstance(comment.parent(), praw.models.Comment) and bot_username.lower() in comment.parent().body.lower() and 'automod' not in str(comment.parent().author).lower():
		requests.post(request_url + "/remove-comment/", {'sub_name': sub_config.subreddit_name, 'comment_id': comment.id})
		return True
        author1 = comment.author  # Author of the top level comment
        comment_word_list = [x.encode('utf-8').strip() for x in comment.body.lower().replace(",", '').replace("\n", " ").replace("\r", " ").replace(".", '').replace("?", '').replace("!", '').replace("[", '').replace("]", " ").replace("(", '').replace(")", " ").replace("*", '').replace("\\", "").replace(">", "").split(" ")]  # all words in the top level comment
	if debug:
		print(" ".join(comment_word_list))
	# Determine if they properly tagged a trade partner
        desired_author2_string = get_desired_author2_name(comment_word_list, bot_username, str(author1))
        if not desired_author2_string:
                handle_no_author2(comment_word_list, comment)
		requests.post(request_url + "/remove-comment/", {'sub_name': sub_config.subreddit_name, 'comment_id': comment.id})
                return True
	# Get an instance of the parent post
	parent_post = comment
	while parent_post.__class__.__name__ == "Comment":
		parent_post = parent_post.parent()
	# Remove comments in giveaway posts
	if "(giveaway)" in parent_post.title.lower():
		print("Removing comment " + str(comment) + " due to parent " + str(parent_post) + " being a giveaway.")
		handle_giveaway(comment)
		requests.post(request_url + "/remove-comment/", {'sub_name': sub_config.subreddit_name, 'comment_id': comment.id})
		return True
	# Remove comment if post is archived
	if parent_post.archived:
		print("Removing comment " + str(comment) + " due to parent " + str(parent_post) + " being archived.")
		requests.post(request_url + "/remove-comment/", {'sub_name': sub_config.subreddit_name, 'comment_id': comment.id})
		return True
	# Remove comment if the author of the post has deleted the post
	if not parent_post.author:
		handle_deleted_post(comment)
		requests.post(request_url + "/remove-comment/", {'sub_name': sub_config.subreddit_name, 'comment_id': comment.id})
		return True
	# Remove comment if neither the person doing the tagging nor the person being tagged are the OP
	if not str(author1).lower() == str(parent_post.author).lower() and not "u/"+str(parent_post.author).lower() == desired_author2_string.lower():
		handle_not_op(comment, str(parent_post.author))
		requests.post(request_url + "/remove-comment/", {'sub_name': sub_config.subreddit_name, 'comment_id': comment.id})
		return True
        correct_reply = find_correct_reply(comment, author1, desired_author2_string)
        if correct_reply:
		# Remove if correct reply is made by someone who cannot leave public commens on the sub
		if correct_reply.banned_by:
			inform_comment_with_filtered_user(comment)
			requests.post(request_url + "/remove-comment/", {'sub_name': sub_config.subreddit_name, 'comment_id': comment.id})
			return True
                author2 = correct_reply.author
		if debug:
			print("Author1: " + str(author1))
			print("Author2: " + str(author2))
                if correct_reply.is_submitter or comment.is_submitter:  # make sure at least one of them is the OP for the post
                        credit_given, author1_count, author2_count = update_database(author1, author2, parent_post.id, comment.id)
                        if credit_given:
                                non_updated_users = update_flair(author1, author2, author1_count, author2_count, sub)
                                inform_giving_credit(correct_reply, non_updated_users)
                        else:
                                inform_credit_already_given(correct_reply)
				requests.post(request_url + "/remove-comment/", {'sub_name': sub_config.subreddit_name, 'comment_id': comment.id})
		return True
        else:  # If we found no correct looking comments, let's come back to it later
		if debug:
			print("No correct looking replies were found")
		return False

def get_desired_author2_name(comment_word_list, bot_username, author_username_string):
	for word in comment_word_list:  # We try to find the person being tagged in the top level comment
		if "u/" in word and bot_username.lower() not in word and 'digitalcodesellbot' not in word and 'uvtrade_bot' not in word:
			desired_author2_string = word
			if desired_author2_string[0] == "/":  # Sometimes people like to add a / to the u/username
				desired_author2_string = desired_author2_string[1:]
			if not desired_author2_string[2:] == author_username_string.lower():
 				return desired_author2_string
	return ""

def handle_no_author2(comment_word_list, comment):
	print("\n\n" + str(time.time()) + "\n" + "Unable to find a username in " + str(comment_word_list) + " for post " + comment.parent().id)
	reply_text = "You did not tag anyone other than this bot in your comment. Please post a new top level comment tagging this bot and the person you traded with to get credit for the trade."
	try:
		if not debug:
			if not silent:
				comment.reply(reply_text)
			else:
				print(reply_text + "\n==========")
		else:
			print(reply_text + "\n==========")
	except Exception as e:  # Comment was probably deleted
		print("\n\n" + str(time.time()) + "\n" + str(e))
		print("handle_no_author2 Comment: " + str(comment))

def handle_deleted_post(comment):
	reply_text = "The OP of this submission has deleted the post. As such, this bot cannot verify that either you or the person you tagged are the OP of this post. No credit can be given for this trade because of this. Please do not delete posts again in the future. Thanks!"
        try:
                if not debug:
                        if not silent:
                                comment.reply(reply_text)
                        else:
                                print(reply_text + "\n==========")
                else:
                        print(reply_text + "\n==========")
        except Exception as e:  # Comment was probably deleted
                print("\n\n" + str(time.time()) + "\n" + str(e))
		print("handle_deleted_post Comment: " + str(comment))

def handle_giveaway(comment):
	reply_text = "This post is marked as a (giveaway). As such, it cannot be used to confirm any transactions as no transactions have occured. Giveaways are not valid for increasing your feedback score. This comment will not be tracked and no feedback will be given."
	try:
		if not debug:
			if not silent:
				comment.reply(reply_text)
			else:
				print(reply_text + "\n==========")
		else:
			print(reply_text + "\n==========")
	except Exception as e:  # Comment was probably deleted
		print("\n\n" + str(time.time()) + "\n" + str(e))
		print("handle_deleted_post Comment: " + str(comment))

def handle_not_op(comment, op_author):
	reply_text = "Neither you nor the person you tagged are the OP of this post so credit will not be given and this comment will no longer be tracked. The original author is " + op_author + ". If you meant to tag someone else, please make a **NEW** comment and tag the correct person (**editing your comment will do nothing**). Thanks!"
        try:
                if not debug:
                        if not silent:
                                comment.reply(reply_text)
                        else:
                                print(reply_text + "\n==========")
                else:
                        print(reply_text + "\n==========")
        except Exception as e:  # Comment was probably deleted
                print("\n\n" + str(time.time()) + "\n" + str(e))
		print("handle_not_op Comment: " + str(comment))

def find_correct_reply(comment, author1, desired_author2_string):
	replies = comment.replies
	try:
		replies.replace_more(limit=None)
	except Exception as e:
		print("Was unable to add more comments down the comment tree when trying to find correct reply with comment: " + str(comment) + " with error: " + str(e))
		return None
	for reply in replies.list():
		potential_author2_string = "u/"+str(reply.author).lower()
		if not potential_author2_string == desired_author2_string:
			continue
                if str(author1).lower() == potential_author2_string:  # They can't get credit for swapping with themselves
                        continue
                return reply
	return None

def inform_comment_with_filtered_user(comment):
	reply_text = "The person you are attempting to confirm a trade with is unable to leave public comments on this sub. The rules state that you should not make a deal with someone who cannot leave a public comment. As such, this trade cannot be counted as the person trying to confirm it cannot leave a public comment."
	try:
		if not debug and not silent:
			comment.reply(reply_text)
		else:
			print(reply_text)
	except Exception as e:
		print("\n\n" + str(time.time()) + "\n" + str(e))  # comment was probably deleted
		print("inform_comment_archived Comment: " + str(comment))

def inform_comment_archived(comment):
	try:
		if not debug:
			word_list = [x.encode('utf-8').strip() for x in comment.body.lower().replace(",", '').replace("\n", " ").replace("\r", " ").replace(".", '').replace("?", '').replace("!", '').replace("[", '').replace("]", " ").replace("(", '').replace(")", " ").replace("*", '').replace("\\", "").split(" ")]
			author2 = get_desired_author2_name(word_list, sub_config.bot_username, str(comment.author))
			if not silent:
				comment.reply(author2 + ", please reply to the comment above this to confirm with your trade partner.\n\nThis comment has been around for more than 3 days without a response. The bot will still track this comment but it will only check it once a day. This means that if your trade partner replies to your comment, it will take up to 24 hours before your comment is confirmed. Please wait that long before messaging the mods for help. If you are getting this message but your partner has already confirmed, please message the mods for assistance.")
			else:
				print("This comment has been around for more than 3 days without a response. The bot will still track this comment but it will only check it once a day. This means that if your trade partner replies to your comment, it will take up to 24 hours before your comment is confirmed. Please wait that long before messaging the mods for help. If you are getting this message but your partner has already confirmed, please message the mods for assistance.")
			requests.post(request_url + "/archive-comment/", {'sub_name': sub_config.subreddit_name, 'comment_id': comment.id})
		else:
			print("This comment has been around for more than 3 days without a response. The bot will still track this comment but it will only check it once a day. This means that if your trade partner replies to your comment, it will take up to 24 hours before your comment is confirmed. Please wait that long before messaging the mods for help. If you are getting this message but your partner has already confirmed, please message the mods for assistance.")
	except Exception as e:
		print("\n\n" + str(time.time()) + "\n" + str(e))  # comment was probably deleted
		print("inform_comment_archived Comment: " + str(comment))

def inform_comment_deleted(comment):
	reply_text = "This comment has been around for more than a month and will no longer be tracked. If you wish to attempt to get trade credit for this swap again, please make a new comment and tag both this bot and your trade partner."
	try:
		if not debug and not silent:
			comment.reply(reply_text)
		else:
			print(reply_text)
	except Exception as e:
		print("\n\n" + str(time.time()) + "\n" + str(e))  # comment was probably deleted
		print("Comment: " + str(comment))

def inform_giving_credit(correct_reply, non_updated_users):
	reply_text = sub_config.confirmation_text
	if non_updated_users:
		reply_text += "\n\n---\n\nThis trade **has** been recorded for **both** users in the database. However, the following user(s) have a total number of" + sub_config.flair_word.lower() + " that is below the threshold of " + str(sub_config.flair_threshold) + " and have **not** had their flair updated:"
		for user, swap_count in non_updated_users:
			reply_text += "\n\n* " + user + " - " + swap_count + sub_config.flair_word
		reply_text += "\n\nFlair for those users will update only once they reach the flair threshold mentioned above."

	try:
		if not debug:
			if not silent:
				correct_reply.reply(reply_text)
			else:
				print(reply_text + "\n==========")
		else:
			print(reply_text + "\n==========")
	except Exception as e:  # Comment was porobably deleted
		print("\n\n" + str(time.time()) + "\n" + str(e))
		print("inform_giving_credit Comment: " + str(correct_reply))

def inform_credit_already_given(correct_reply):
	credit_given_message = "You already got credit for this trade. This is because credit is only given once per partner per thread. If you already received credit with this user on this thread, please do not message the mods asking for an exception. Only message the mods if you think this is an error."
	try:
		if not debug and not silent:
			correct_reply.reply(credit_given_message)
		else:
			print(credit_given_message + "\n==========")
	except Exception as e:  # Comment was probably deleted
		print("\n\n" + str(time.time()) + "\n" + str(e))
		print("inform_credit_already_given Comment: " + str(correct_reply))

def main():
	reddit = praw.Reddit(client_id=sub_config.client_id, client_secret=sub_config.client_secret, user_agent='UserAgent', username=sub_config.bot_username, password=sub_config.bot_password)
	sub = reddit.subreddit(sub_config.subreddit_name)

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
			requests.post(request_url + "/archive-comment/", {'sub_name': sub_config.subreddit_name, 'comment_id': comment.id})
			continue
		handeled = handle_comment(comment, sub_config.bot_username, sub)
		time_made = comment.created
		# if this comment is more than three days old and we didn't find a correct looking reply
		if time.time() - time_made > 3 * 24 * 60 * 60 and not handeled:
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
			except praw.exceptions.ClientException as e:
				print("Could not 'refresh' archived comment: " + str(comment)+ " with exception: \n    " + str(type(e).__name__) + " - " + str(e) + "\n    Removing comment...\n")
				requests.post(request_url + "/remove-comment/", {'sub_name': sub_config.subreddit_name, 'comment_id': comment.id})
	                        continue
			except Exception as e:
				print("Could not 'refresh' archived comment: " + str(comment)+ " with exception: \n    " + str(type(e).__name__) + " - " + str(e))
				continue
			time_made = comment.created
			if time.time() - time_made > 30 * 24 * 60 * 60:  # if this comment is more than thirty days old
				inform_comment_deleted(comment)
				requests.post(request_url + "/remove-comment/", {'sub_name': sub_config.subreddit_name, 'comment_id': comment.id})
			else:
				handle_comment(comment, sub_config.bot_username, sub)
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
		trades = requests.post(request_url + "/get-summary/", {'sub_name': sub_config.database_name, 'username': username}).json()['data']
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
			if "LEGACY TRADE" in trade:
				legacy_count += 1
			else:
				trade_partner = trade.split(" - ")[0]
				trade_partner_count = len(requests.post(request_url + "/get-summary/", {'sub_name': sub_config.database_name, 'username': trade_partner}).json()['data'])
				trade_url = trade.split(" - ")[1]
				try:
					trade_url_sub = trade_url.split("/")[4]
				except:
					print("Error getting trade sub url from " + trade_url)
					continue
				trade_url_id = trade_url.split("/")[6]
				final_text += "*  [" + trade_url_sub + "/" + trade_url_id  + "](https://redd.it/" + trade_url_id  + ") - u/" + trade_partner + " (Has " + str(trade_partner_count) + " " + sub_config.flair_word + ")" + "\n\n"

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

if __name__ == "__main__":
	main()
