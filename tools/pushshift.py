import praw
import sys
sys.path.insert(0, '.')
import config
import swap

from collections import defaultdict
import time
import re
import requests

request_url = "http://192.168.0.155:8000"

feedback_sub_name = "WatchExchangeFeedback".lower()
sub_name = "WatchExchange".lower()

def GetIdsFromPushshift(feedback_sub_name):
	print("Grabbing IDs from Pushshift")
	ids = set()
	authors = set()
	count = 0
	after = 0

	r = requests.get("https://api.pushshift.io/reddit/submission/search?subreddit=" + feedback_sub_name + "&after=" + str(after) + "&before=" + str(int(time.time()))  + "&size=100")
	data = r.json()['data']
	while data:
		for item in data:
			count += 1
			authors.add(str(item['author']).lower())

			item_time = 0
			if 'retrieved_on' in item:
				item_time = item['retrieved_on']
			if not 'retrieved_on' in item and 'created_utc' in item:
				item_time = item['created_utc']
			if item_time > after:
				after = item_time

			if 'id' in item:
				ids.add(item['id'])

#			if 'selftext' in item:
#				match = re.compile("r/" + feedback_sub_name + "/comments/(.*?)/")
#				found = match.findall(item['selftext'].lower())
#				for id_found in found:
#					ids.add(id_found)

			if (count % 50 == 0):
				print("Total IDs Found: " + str(len(ids)))
				print("Current Date: " + time.strftime('%m/%d/%Y %H:%M:%S',  time.gmtime(after)))

		time.sleep(1)
		r = requests.get("https://api.pushshift.io/reddit/submission/search?subreddit=" + feedback_sub_name + "&after=" + str(after) + "&before=" + str(int(time.time()))  + "&size=100")
		data = r.json()['data']
	return ids, authors

def GetIdsFromReddit(sub, authors, ids):
	print("Grabbing IDs from Reddit")
	submission_count = 0
	for submission in sub.new(limit=1):
		ids.add(submission.id)
		authors.add(str(submission.author).lower())
		match = re.compile("\/*u\/([A-Za-z0-9_-]+)")
		found = match.findall(submission.title)
		if found:
			authors.add(str(found[0]).lower())
		submission_count += 1
		if submission_count % 50 == 0:
			print("Finished checking " + str(submission_count) + " search results from reddit.")

	author_count = 0
	for author in authors:
		author_count += 1
		time.sleep(0.5)
		for submission in sub.search("author:"+author):
			ids.add(submission.id)
		for submission in sub.search(author):
			ids.add(submission.id)
		if author_count % 10 == 0:
			print("Finished checking " + str(author_count) + " out of " + str(len(authors))  + " authors from reddit.")
	print("Found a total of " + str(len(ids)) + " post ids.")


def GetUserCounts(authors, ids, sub_config):
	print("Getting user counts from Reddit")
	d = defaultdict(lambda: [])

	count = 0

	for id in ids:
		time.sleep(0.5)
		try:
			submission = reddit.submission(id=id)
		except Exception as e:
			print("Found exception " + str(e) + "\n    Sleeping for 20 seconds...")
			time.sleep(20)
			submission = reddit.submission(id=id)
		author = str(submission.author).lower()
		author2 = ""
                match = re.compile("\/*u\/([A-Za-z0-9_-]+)")
		found = match.findall(submission.title.lower())
		if found:
			author2 = found[0]
		else:
			for word in submission.title.lower().split(" "):
				if word in authors:
					author2 = word
					break
		# Not able to find a author in the title
		if not author2:
			continue
		if any(word in ["avoid", "bad", "difficult", "can't", "misrepresent", "waste", "scammer", "negative"] for word in submission.title.lower().split(" ")):
			# Negative Feedback
			continue
#		for comment in submission.comments:
#			giver = str(comment.author).lower()
#			comment_text = comment.body
#			while(" " in comment_text):
#				comment_text = comment_text.replace(" ", "")
#			for i in range(10):
#				comment_text = comment_text.replace(str(i), "1")
#			comment_text = comment_text.replace("1+", "+1")
#			if "+1" in comment_text:
#				d[author].append(giver + " - https://www.reddit.com" + str(comment.permalink))
		try:
			d[author.lower()].append(author2.lower() + " - https://www.reddit.com" + str(submission.permalink))
			d[author2.lower()].append(author.lower() + " - https://www.reddit.com" + str(submission.permalink))
		except Exception as e:
			print("Error encoding some text: ")
			try:
				print(author.lower())
				print(author2.lower())
				print(submission.permalink)
			except:
				print("Cant manage to print anything...")
		count += 1
		if count % 50 == 0:
			print("Finished looking at submission number " + str(count) + " out of " + str(len(ids)) + " submissions.")


	total_confirmations = sum([len(d[author]) for author in d])
	total_users = len(d.keys())
	print("Found " + str(total_confirmations) + " confirmations across " + str(total_users) + " total users.")
	print(d)
	return d

def UpdateDatabase(sub_name, users_to_confirmations):
	print("Updatind Database for all users...")
	count = 0
	for user in users_to_confirmations:
		confirmation_text_list = ",".join(users_to_confirmations[user])
		requests.post(request_url + "/add-batch-swap/", {'sub_name': sub_name, 'username': user, 'swap_text': confirmation_text_list})
		count += 1
		if count % 10 == 0:
			print("Finished updating database for " + str(count) + " users out of " + str(len(users_to_confirmations)) + " users.")

def UpdateFlairs(sub, sub_config, users):
	print("Updating flair for all users...")
	count = 0
        for user in users:
		r = requests.post(request_url + "/get-summary/", {'sub_name': sub_config.subreddit_name, 'username': user.lower()})
                swap_count = str(len(r.json()['data']))
                try:
                        swap.update_single_user_flair(sub, sub_config, user, swap_count, [])
                except Exception as e:
                        print("Found exception " + str(e) + "\n    Sleeping for 20 seconds...")
                        time.sleep(20)
			try:
	                        swap.update_single_user_flair(sub, sub_config, user, swap_count, [])
			except Exception as e:
				print("Unable to assign flair to " + user + ":\n    " + str(e))
                time.sleep(0.5)
		count += 1
		if count % 25 == 0:
			print("Finished assigning flair for " + str(count) + " users out of " + str(len(users)) + " users.")

sub_config = config.Config(sub_name)
reddit = praw.Reddit(client_id=sub_config.client_id, client_secret=sub_config.client_secret, user_agent='UserAgent', username=sub_config.bot_username, password=sub_config.bot_password)
sub = reddit.subreddit(sub_config.subreddit_name)
feedback_sub = reddit.subreddit(feedback_sub_name)

#ids, authors = GetIdsFromPushshift(feedback_sub_name)
ids = set([])
authors = set(["doublecheezluva".lower()])
GetIdsFromReddit(feedback_sub, authors, ids)
users_to_confirmations = GetUserCounts(authors, ids, sub_config)
UpdateDatabase(sub_config.subreddit_name, users_to_confirmations)
UpdateFlairs(sub, sub_config, users_to_confirmations.keys())
