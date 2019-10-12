import time
import urllib
import requests
import re
import json
import praw
import time
import datetime

debug = False

sub_name = "pkmntcgtrades"
sub_name = "vinylcollectors"
sub_name = 'mousemarket'
sub_name = 'digitalcodesell'
f = open("config/" + sub_name + "-config.txt", "r")
info = f.read().splitlines()
f.close()

subreddit_name = info[0].split(":")[1]
client_id = info[1].split(":")[1]
client_secret = info[2].split(":")[1]
bot_username = info[3].split(":")[1]
bot_password = info[4].split(":")[1]
try:
	swap_word = " " + info[5].split(":")[1]
except:
	swap_word = " Swaps"
try:
	mod_flair_word = " " + info[6].split(":")[1]
except:
	mod_flair_word = ""

FNAME_comments = 'database/active_comments-' + subreddit_name + '.txt'
FNAME_swaps = 'database/swaps-' + subreddit_name + ".json"
FNAME_archive = 'database/archive-' + subreddit_name + '.txt'

# IDK, I needed this according to stack overflow.
def ascii_encode_dict(data):
        ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
        return dict(map(ascii_encode, pair) for pair in data.items())

# Function to load the swap DB into memory
def get_swap_data():
        with open(FNAME_swaps) as json_data: # open the funko-shop's data
                funko_store_data = json.load(json_data, object_hook=ascii_encode_dict)
        return funko_store_data

def update_database(author1, author2, swap_data, message):
        author1 = str(author1).lower()  # Create strings of the user names for keys and values
        author2 = str(author2).lower()

        # Default generic value for swaps
	message = author2 + " - " + message
	if author1 not in swap_data:  # If we have not seen this user before in swap, make a new entry for them
                swap_data[author1] = [message]
        else:  # If we have seen them before, we want to make sure they didnt already get credit for this swap (same $
                if message in swap_data[author1]:
                        return False
                swap_data[author1].append(message)
        return True  # If all went well, return true

# Writes the json local file... dont touch this.
def dump_json(swap_data):
        with open(FNAME_swaps, 'w') as outfile:  # Write out new data
                outfile.write(str(json.dumps(swap_data))
                        .replace("'", '"')
                        .replace(', u"', ', "')
                        .replace('[u"', '["')
                        .replace('{u"', '{"')
                        .encode('ascii','ignore'))

def reassign_all_flair(sub, data):
	for user in data:
		count = len(data[user])
		if count < 10:
			continue
                sub.flair.set(user, str(count) + swap_word, str(count))
                print(user + " - " + str(count))
		time.sleep(.25)
#		return

def add_legacy_trade(user, count, data):
	for i in range(count):
		data[user].append('LEGACY TRADE')
	update_flair(user, str(len(data[user])))
	dump_json(data)

def update_flair(user, count):
        sub.flair.set(str(user).lower(), count + swap_word, count)
        print(user + " - " + count)

def add_all_flair(data, sub):
	new_data = {}
	bad_count = 0
	good_count = 0
	total_swaps = 0
	for user in data:
		count = str(len(data[user]))
		try:
			update_flair(user, count)
			new_data[user] = data[user]
			good_count += 1
			total_swaps += int(count)
		except Exception as e:
			print(user + " IS NOT A USER")
			bad_count += 1
	print("users found: " + str(good_count))
	print("users removed: " + str(bad_count))
	print("total swaps: " + str(total_swaps))

def add_feedback_from_posts(reddit, sub, ids):
	swap_data = get_swap_data()
	for id in ids:
		submission = reddit.submission(id=str(id))
		author1 = str(submission.author)
		comments = submission.comments
#		children = []
#		for comment in comments:
#			for child in comment.replies:
#				print(child)
#				children.append(child)
		for comment in comments:
			message = "https://www.reddit.com" + str(urllib.quote(comment.permalink.encode('utf-8'), safe=':/'))
			author2 = str(comment.author)
			print(author1 + " -> " + author2)
			print("    " + message)
			status = update_database(author1, author2, swap_data, message)
			if not status:
				print("Found duplicate post")

#		for comment in children:
#			print(comment)
#			message = "https://www.reddit.com" + str(urllib.quote(comment.permalink.encode('utf-8'), safe=':/'))
#			author2 = str(comment.author)
#			print(author1 + " -> " + author2)
#			print("    " + message)
#			status = update_database(author1, author2, swap_data, message)
#			if not status:
#				print("Found duplicate post")
	        count = str(len(swap_data[author1.lower()]))
		update_flair(author1.lower(), count)
	dump_json(swap_data)



def add_feedback_from_vinylcollectors_posts(reddit, sub):
	mods = [str(x) for x in sub.moderator()]
	mods.append('ferricyanide')
	mods.append('u/ferricyanide')
	post_ids = ['avq2s4', '9baxki', '7zeg1o', '6vmdr4', '5vzo0d', '53qleg', '4i1q6w']
#	post_ids = ['6vmdr4', '5vzo0d', '53qleg', '4i1q6w']
	swap_data = get_swap_data()
	to_handle_later = []
	f = open("tmp.txt", 'r')
	comment_ids = f.read().splitlines()
	f.close()
	print("have to look at " + str(len(comment_ids)) + " comments")
	count = 0
	for id in comment_ids:
		count += 1
		comment = reddit.comment(id)
		message = "https://www.reddit.com" + str(urllib.quote(comment.permalink.encode('utf-8'), safe=':/'))
                body = comment.body.lower().replace(">", "").replace("<", "")
		link_regex = re.compile('(https://www.reddit.com/r/vinylcollectors/comments/.*?/.*?/)')
		links = link_regex.findall(body)
		for found in links:
			body = body.replace(found, "")
		body = body.replace('"', "").replace("'", "").replace("u/ ", "u/")
		regex = re.compile('(u\/[A-Za-z0-9_-]+)')
		matches = regex.findall(body)
		regex = re.compile('(user\/[A-Za-z0-9_-]+)')
		matches += [x.replace("user/", "u/") for x in regex.findall(body)]
		regex = re.compile('user (.+?) ')
		matches += ["u/"+x for x in regex.findall(body)]
		author2 = str(comment.author).lower()
		author1 = "a"
		print("\n========\n" + body + " -> " + message) #"https://www.reddit.com/r/vinylcollectors.com/comments/" + id + "/-/" + comment.id)
		if len(body.split(" ")) < 2:
			continue
		if len(body) < 22:
			continue
		if 'link to thread please?' in body:
			continue
		if matches and 'negative' not in body:
			for author1 in matches:
				if 'u//u/' in author1:
					author1 = author1[3:]
				user = ""
				if not 'prompt payment' in body and not "am satisfied with" in body and not "positive" in body and not 'postive' in body and not 'received' in body and not 'sold to' in body:
					user = raw_input(author1 + " >> ")
				if user:
					continue
		                print(author1 + " -> " + str(author2))
		                print("    " + message)
                		status = update_database(author1, author2, swap_data, message)
        			if not status:
					print("Found duplicate post")
		else:
			if str(comment.author) in mods and 'positive' not in body:
				continue
			while author1:
				author1 = raw_input(">> ")
				if not author1:
					continue
				author1 = "u/" + author1.lower()
		                print(author1 + " -> " + str(author2))
		                print("    " + message)
                		status = update_database(author1, author2, swap_data, message)
        			if not status:
					print("Found duplicate post")
		dump_json(swap_data)
		f = open("tmp.txt", 'w')
		f.write("\n".join(comment_ids[count:]))
		f.close()

reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent='UserAgent', username=bot_username, password=bot_password)
sub = reddit.subreddit(subreddit_name)

#add_feedback_from_vinylcollectors_posts(reddit, sub)
#add_feedback_from_posts(reddit, sub, ['9erx6e', '84hbfq', '5wqjdl', '4yj732'])
#add_all_flair(get_swap_data(), sub)
#reassign_all_flair(sub, get_swap_data())
#add_legacy_trade('Hannibal_Hector'.lower(), 40, get_swap_data())
sub.flair.set('totallynotregexr', mod_flair_word + ' 9001 Swaps', flair_template_id='33eb2ccc-4cb5-11e9-8fc4-0ed4d82ea13a')
