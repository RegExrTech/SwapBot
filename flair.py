import urllib
import requests
import re
import json
import praw
import time
import datetime

debug = False

f = open("config/pkmntcgtrades-config.txt", "r")
info = f.read().splitlines()
f.close()

subreddit_name = info[0]
client_id = info[1]
client_secret = info[2]
bot_username = info[3]
bot_password = info[4]
try:
	swap_word = " " + info[5]
except:
	swap_word = " Swaps"
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

def reassign_all_flair(sub):
        flairs = sub.flair(limit=None)
        # Loop over each author and change their flair
        for flair in flairs:
		text = flair['flair_text']
		if text and swap_word in text:
			continue
                css = flair['flair_css_class']
		try:
			css = str(int(css))
		except:
#			print("Found flair " + str(css) + " for user " + str(flair['user']))
			css = "0"
                print(str(flair['user']) + " - " + css + swap_word)
                sub.flair.set(str(flair['user']).lower(), css + swap_word, css)

def update_flair(user, count):
        print(user + " - " + count)
        sub.flair.set(str(user).lower(), count + swap_word, count)

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

reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent='UserAgent', username=bot_username, password=bot_password)
sub = reddit.subreddit(subreddit_name)

add_feedback_from_posts(reddit, sub, ['9erx6e', '84hbfq', '5wqjdl', '4yj732'])
#reassign_all_flair(sub)
