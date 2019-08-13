import re
import json
import praw
import time
import datetime
import argparse

try:
	parser = argparse.ArgumentParser()
	parser.add_argument('config_file_name', metavar='C', type=str)
	args = parser.parse_args()
	fname = 'config/' + args.config_file_name
except: # if no cmnd line args are passed in, assume they are still using old file structure
	fname = "config.txt"

debug = False

f = open(fname, "r")
info = f.read().splitlines()
f.close()

# Pad out the config values in case optional options are not present
for i in range(7 - len(info)):
	info.append("")

subreddit_name = info[0]
client_id = info[1]
client_secret = info[2]
bot_username = info[3]
bot_password = info[4]
if info[5]:
	flair_word = " " + info[5]
else:
	flair_word = " Swaps"
if info[6]:
	mod_flair_word = info[6] + " "
else:
	mod_flair_word = ""

FNAME_comments = 'database/active_comments-' + subreddit_name + '.txt'
FNAME_swaps = 'database/swaps-' + subreddit_name + ".json"
FNAME_archive = 'database/archive-' + subreddit_name + '.txt'
check_time = datetime.datetime.utcnow().time()

# Checks if the time at script start up is between two desired times
def is_time_between(begin_time, end_time):
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

# Gets the previously seen comments to check again
def get_prev_ids():
	f = open(FNAME_comments, "r")
	ids = f.read().splitlines()
	f.close()
	return ids

# Returns the list of archived comments to check
def get_archived_ids():
	f = open(FNAME_archive, "r")
	ids = f.read().splitlines()
	f.close()
	return ids

# IDK, I needed this according to stack overflow.
def ascii_encode_dict(data):
	ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
	return dict(map(ascii_encode, pair) for pair in data.items())

# Function to load the swap DB into memory
def get_swap_data():
	with open(FNAME_swaps) as json_data: # open the funko-shop's data
		funko_store_data = json.load(json_data, object_hook=ascii_encode_dict)
	return funko_store_data

# Dump the comment Ids
def dump(to_write):
	f = open(FNAME_comments, "w")
	f.write("\n".join(to_write))
	f.close()

# Add new comments to the archived comments
def add_to_archive(archive):
	prev_ids = get_archived_ids()
	f = open(FNAME_archive, 'w')
	f.write("\n".join(list(set(archive+prev_ids))))
	f.close()

# Dump the entire archive list back into the file
def dump_archive(archive):
	f = open(FNAME_archive, "w")
	f.write("\n".join(list(set(archive))))
	f.close()

# Writes the json local file... dont touch this.
def dump_json(swap_data):
	with open(FNAME_swaps, 'w') as outfile:  # Write out new data
		outfile.write(str(json.dumps(swap_data))
			.replace("'", '"')
			.replace(', u"', ', "')
			.replace('[u"', '["')
			.replace('{u"', '{"')
			.encode('ascii','ignore'))

# Method for giving credit to users when they do a trade.
# Returns True if credit was given, False otherwise
def update_database(author1, author2, swap_data, post_id):
	author1 = str(author1).lower()  # Create strings of the user names for keys and values
	author2 = str(author2).lower()

	# Default generic value for swaps
	message = " - https://www.reddit.com/r/" + subreddit_name + "/comments/" + post_id
	if author1 not in swap_data:  # If we have not seen this user before in swap, make a new entry for them
		swap_data[author1] = [author2 + message]
	else:  # If we have seen them before, we want to make sure they didnt already get credit for this swap (same user and same post)
		if author2 + message in swap_data[author1]:
			return False
		swap_data[author1].append(author2 + message)
	if author2 not in swap_data:  # Same as above but for the other user. too lazy to put this in a nice loop and the user case will never expand past two users
                swap_data[author2] = [author1 + message]
        else:
		if author1 + message in swap_data[author2]:
			return False
                swap_data[author2].append(author1 + message)
	return True  # If all went well, return true

def update_flair(author1, author2, sub, swap_data):
	mods = [str(x).lower() for x in sub.moderator()]
	author1 = str(author1).lower()  # Create strings of the user names for keys and values
	author2 = str(author2).lower()

	flairs = sub.flair(limit=None)
	# Loop over each author and change their flair
	for author in [author1, author2]:
		print("attempting to assign flair for " + author)
		swap_count = str(len(swap_data[author]))
		if not debug:
			if author in mods:
				sub.flair.set(author, mod_flair_word + swap_count + flair_word, swap_count)
			else:
				sub.flair.set(author, swap_count + flair_word, swap_count)
		else:
			print("Assigning flair " + swap_count + " to user " + author)
			print("length of swap_data: " + str(len(swap_data[author])))
			print(swap_data[author])
			print("==========")

def set_active_comments_and_messages(reddit, comments, messages):
	ids = get_prev_ids()  # Ids of previously seen comments that have not been finished
	# Get comments from locally saved ids
        for comment_id in ids:
                try:
                        comments.append(reddit.comment(comment_id))
                except:  # If we fail, the user deleted their comment or account, so skip
                        pass

        # Get comments from username mentions
	to_mark_as_read = []
	try:
		for message in reddit.inbox.unread():
			to_mark_as_read.append(message)
        	        if message.was_comment and message.subject == "username mention" and (not str(message.author).lower() == "automoderator"):
                	        try:
                        	        comments.append(reddit.comment(message.id))
	                        except:  # if this fails, the user deleted their account or comment so skip it
        	                        pass
                	elif not message.was_comment:
                        	messages.append(message)
	except:
		print("Failed to get next message from unreads. Ignoring all unread messages and will try again next time.")

	if not debug:
		for message in to_mark_as_read:
			try:
				message.mark_read()
			except:
				print("Unable to mark message as read. Leaving it as is.")

        comments = list(set(comments))  # Dedupe just in case we get duplicates from the two sources

def set_archived_comments(reddit, comments):
	ids = get_archived_ids()
	for comment_id in ids:
                try:
                        comments.append(reddit.comment(comment_id))
                except:  # If we fail, the user deleted their comment or account, so skip
                        pass
	comments = list(set(comments))

def handle_comment(comment, bot_username, swap_data, sub, to_write):
	# If this is someone responding to a tag by tagging the bot, we want to ignore them.
	if isinstance(comment.parent(), praw.models.Comment) and bot_username in comment.parent().body and 'automod' not in str(comment.parent().author).lower():
		return
        author1 = comment.author  # Author of the top level comment
        comment_word_list = [x.encode('utf-8').strip() for x in comment.body.lower().replace(",", '').replace("\n", " ").replace("\r", " ").replace(".", '').replace("?", '').replace("!", '').replace("[", '').replace("]", " ").replace("(", '').replace(")", " ").replace("*", '').replace("\\", "").split(" ")]  # all words in the top level comment
	if debug:
		print(" ".join(comment_word_list))
# Had to comment this out because it will post a comment every time it runs.
# If I can figure out how to get it to reply only once, this will be really useful.
#	if any('https://wwwredditcom/user/' in s for s in comment_word_list):
#		if not debug:
#			comment.reply("It looks like you might have made a mistake in how you tagged your trade partner. You added their reddit user name as a link rather than as a tag. Pleae **EDIT** this comment and remove their username, then retype it (do not copy and paste their name) to look like 'u/SomeUsername' and they shoud be properly tagged. I'll do my best to track this comment anyway, but please try to fix your tag. Thanks!")
#		else:
#			print("    It looks like you might have made a mistake in how you tagged your trade partner. You added their reddit user name as a link rather than as a tag. Pleae **EDIT** this comment and remove their username, then retype it (do not copy and paste their name) to look like 'u/SomeUsername' and they shoud be properly tagged. I'll do my best to track this comment anyway, but please try to fix your tag. Thanks!")
        desired_author2_string = get_desired_author2_name(comment_word_list, bot_username, str(author1))
        if not desired_author2_string:
                handle_no_author2(comment_word_list, comment)
                return
        correct_reply = find_correct_reply(comment, author1, desired_author2_string)
        if correct_reply:
                author2 = correct_reply.author
		if debug:
			print("Author1: " + str(author1))
			print("Author2: " + str(author2))
                if correct_reply.is_submitter or comment.is_submitter:  # make sure at least one of them is the OP for the post
			comment_to_check = comment
			while comment_to_check.__class__.__name__ == "Comment":  # Ensures we actually get the id of the parent POST and not just a parent comment
				comment_to_check = comment_to_check.parent()
                        credit_give = update_database(author1, author2, swap_data, comment_to_check.id)
                        if credit_give:
                                inform_giving_credit(correct_reply)
                                update_flair(author1, author2, sub, swap_data)
                        else:
                                inform_credit_already_give(correct_reply)
        else:  # If we found no correct looking comments, let's come back to it later
		if debug:
			print("No correct looking replies were found")
                to_write.append(str(comment.id))

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
			comment.reply("You did not tag anyone other than this bot in your comment. Please post a new top level comment tagging this bot and the person you traded with to get credit for the trade.")
		else:
				print("You did not tag anyone other than this bot in your comment. Please post a new top level comment tagging this bot and the person you traded with to get credit for the trade." + "\n==========")
	except Exception as e:  # Comment was probably deleted
		print("\n\n" + str(time.time()) + "\n" + str(e))

def find_correct_reply(comment, author1, desired_author2_string):
	replies = comment.replies
	replies.replace_more(limit=None)
	for reply in replies.list():
# Commented this out for now. Sometimes people say something other than confirmed but it has the same idea behind it
# So as long as the person replying is the person being tagged, no reason to not give them credit, really.
#		if not 'confirm' in reply.body.lower():  # if a reply does not say confirm, skip it
#			continue
		potential_author2_string = "u/"+str(reply.author).lower()
		if not potential_author2_string == desired_author2_string:
			continue
                if str(author1).lower() == potential_author2_string:  # They can't get credit for swapping with themselves
                        continue
                return reply
	return None

def inform_comment_archived(comment, to_archive):
	try:
		if not debug:
			comment.reply("This comment has been around for more than 3 days without a response. The bot will still track this comment but it will only check it once a day. This means that if your trade partner replies to your comment, it will take up to 24 hours before your comment is confirmed. Please wait that long before messaging the mods for help. If you are getting this message but your partner has already confirmed, please message the mods for assistance.")
			to_archive.append(comment.id)
		else:
			print("This comment has been around for more than 3 days without a response. The bot will still track this comment but it will only check it once a day. This means that if your trade partner replies to your comment, it will take up to 24 hours before your comment is confirmed. Please wait that long before messaging the mods for help. If you are getting this message but your partner has already confirmed, please message the mods for assistance.")
	except Exception as e:
		print("\n\n" + str(time.time()) + "\n" + str(e))  # comment was probably deleted


def inform_comment_deleted(comment):
	try:
		if not debug:
			comment.reply("This comment has been around for more than a month and will no longer be tracked. If you wish to attempt to get trade credit for this swap again, please make a new comment and tag both this bot and your trade partner.")
		else:
			print("This comment has been around for more than a month and will no longer be tracked. If you wish to attempt to get trade credit for this swap again, please make a new comment and tag both this bot and your trade partner.")
	except Exception as e:
		print("\n\n" + str(time.time()) + "\n" + str(e))  # comment was probably deleted

def inform_giving_credit(correct_reply):
	try:
		if not debug:
			correct_reply.reply("Added")
		else:
			print("Added" + "\n==========")
	except Exception as e:  # Comment was porobably deleted
		print("\n\n" + str(time.time()) + "\n" + str(e))

def inform_credit_already_give(correct_reply):
	try:
		if not debug:
			correct_reply.reply("You already got credit for this trade. Please contact the moderators if you think this is an error.")
		else:
			print("You already got credit for this trade. Please contact the moderators if you think this is an error." + "\n==========")
	except Exception as e:  # Comment was probably deleted
		print("\n\n" + str(time.time()) + "\n" + str(e))

def main():
	# We want to give ourselves some buffer time during archive run, so we do't run for ten minutes after
	# archive run.
	if is_time_between(datetime.time(2,3), datetime.time(2,9)) and not debug:
		return
	reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent='UserAgent', username=bot_username, password=bot_password)
	sub = reddit.subreddit(subreddit_name)

	swap_data = get_swap_data()  # Gets the swap data for all users
	comments = []  # Stores comments from both sources of Ids
        messages = []  # Want to catch everything else for replying
	to_write = []  # What we will eventually write out to the local file
	to_archive = [] # For comments that are more than 3 days old (to be checked later)
	set_active_comments_and_messages(reddit, comments, messages)

	# Process comments
	if debug:
		print("Looking through active comments...")
	for comment in comments:
		try:
			comment.refresh()  # Don't know why this is required but it doesnt work without it so dont touch it
		except: # if we can't refresh a comment, archive it so we don't waste time on it.
			print("Could not 'refresh' comment: " + str(comment))
			to_archive.append(str(comment.id))
			continue
		time_made = comment.created
		if time.time() - time_made > 3 * 24 * 60 * 60:  # if this comment is more than three days old
			inform_comment_archived(comment, to_archive)
		else:
			handle_comment(comment, bot_username, swap_data, sub, to_write)
	if not debug:
		dump(to_write)  # Save off any unfinished tags
		if len(to_archive) > 0: # If we have comments to archive, dump them off
			add_to_archive(to_archive)

	# If it is between 00:00 and 00:02 UTC, check the archived comments
	if is_time_between(datetime.time(2,0), datetime.time(2,2)) or debug:
#	if True:
		print("Looking through archived comments...")
		comments = []
		to_write = []  # What we will eventually write out to the local file
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
			else:
				handle_comment(comment, bot_username, swap_data, sub, to_write)

		if not debug:
			dump_archive(to_write)

	if not debug:
		dump_json(swap_data)

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
					message.reply("Hi there,\n\nYou did not specify a username to check. Please ensure that you have a user name, in the body of the message you just sent me. Please feel free to try again. Thanks!")
				except Exception as e:
					print("Could not reply to message with error...")
					print("    " + str(e))
			else:
				print("Hi there,\n\nYou did not specify a username to check. Please ensure that you have a user name in the body of the message you just sent me. Please feel free to try again. Thanks!" + "\n==========")
			continue
		final_text = ""
		try:
			trades = swap_data[username]
		except:  # if that user has not done any trades, we have no info for them.
			if not debug:
				try:
					message.reply("Hello,\n\nu/" + username + " has not had any swaps yet.")
				except Exception as e:
					print("Could not reply to message with error...")
					print("    " + str(e))
			else:
				print("Hello,\n\nu/" + username + " has not had any swaps yet." + "\n==========")
			continue

		legacy_count = 0  # Use this to track the number of legacy swaps someone has
		for trade in trades:
			if trade == "LEGACY TRADE":
				legacy_count += 1
			else:
				final_text += "*  u/" + trade + "\n\n"

		if legacy_count > 0:
			final_text = "* " + str(legacy_count) + " Legacy Trades (trade done before this bot was created)\n\n" + final_text

		if len(trades) == 0:
			if not debug:
				try:
					message.reply("Hello,\n\nu/" + username + " has not had any swaps yet.")
				except Exception as e:
					print("Could not reply to message with error...")
					print("    " + str(e))
			else:
				print("Hello,\n\nu/" + username + " has not had any swaps yet." + "\n==========")
		else:
			if not debug:
				try:
					message.reply("Hello,\n\nu/" + username + " has had the following " + str(len(trades)) + " swaps:\n\n" + final_text)
				except Exception as e:
					print("Could not reply to message with error...")
					print("    " + str(e))
			else:
				print("Hello,\n\nu/" + username + " has had the following " + str(len(trades)) + " swaps:\n\n" + final_text + "\n==========")

main()
