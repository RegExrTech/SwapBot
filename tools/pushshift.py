import praw
import sys
sys.path.insert(0, '.')
import config
import swap

from collections import defaultdict
import time
import re
import requests

request_url = "http://192.168.0.248:8000"

feedback_sub_name = "ygofeedback"
sub_name = "YGOMarketplace"

def GetIdsFromPushshift(feedback_sub_name):
	print("Grabbing IDs from Pushshift")
	ids = set()
	authors = set()
	count = 0
	after = time.time()

	r = requests.get("https://api.pushshift.io/reddit/submission/search?subreddit=" + feedback_sub_name + "&after=" + str(after) + "&before=1594612800&size=100")
	data = r.json()['data']

	while data:
		for item in r.json()['data']:
			if 'retrieved_on' in item and  item['retrieved_on'] > after:
				after = item['retrieved_on']
			if 'id' in item:
				ids.add(item['id'])
			if 'selftext' in item:
				match = re.compile("r/" + feedback_sub_name + "/comments/(.*?)/")
				found = match.findall(item['selftext'].lower())
				for id_found in found:
					ids.add(id_found)
			if (count % 50 == 0) and 'retrieved_on' in item:
				try:
					print("Total IDs Found: " + str(len(ids)))
					print("Current Date: " + time.strftime('%m/%d/%Y %H:%M:%S',  time.gmtime(item['retrieved_on'])))
				except:
					pass
			count += 1
		r = requests.get("https://api.pushshift.io/reddit/submission/search?subreddit=" + feedback_sub_name + "&after=" + str(after) + "&before=1594612800&size=100")
		data = r.json()['data']

	return ids, authors

def GetIdsFromReddit(sub, authors):
	print("Grabbing IDs from Reddit")
	ids = []
	submission_count = 0
	for submission in sub.new(limit=1000):
		ids.append(submission.id)
		authors.append(str(submission.author))
		submission_count += 1
		if submission_count % 50 == 0:
			print("Finished checking " + str(submission_count) + " search results from reddit.")

	author_count = 0
	for author in authors:
		time.sleep(0.5)
		for submission in sub.search("author:"+author):
			ids.append(submission.id)
		if author_count % 10 == 0:
			print("Finished checking " + str(author_count) + " authors from reddit.")

	return ids

def GetUserCounts(ids, sub_config):
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
		for comment in submission.comments:
			giver = str(comment.author).lower()
			comment_text = comment.body
			while(" " in comment_text):
				comment_text = comment_text.replace(" ", "")
			for i in range(10):
				comment_text = comment_text.replace(str(i), "1")
			comment_text = comment_text.replace("1+", "+1")
			if "+1" in comment_text:
				d[author].append(giver + " - https://www.reddit.com" + str(comment.permalink))
		count += 1
		if count % 50 == 0:
			print("Finished looking at submission number " + str(count) + " out of " + str(len(ids)) + " submissions.")


	total_confirmations = sum([len(d[author]) for author in d])
	total_users = len(d.keys())
	print("Found " + str(total_confirmations) + " confirmations across " + str(total_users) + " total users.")
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

def UpdateFlairs(sub, sub_config, users_to_confirmations):
	print("Updating flair for all users...")
	count = 0
        for author in users_to_confirmations:
		r = requests.post(request_url + "/get-summary/", {'sub_name': sub_config.subreddit_name, 'username': author.lower()})
                swap_count = str(len(r.json()['data']))
                try:
                        swap.update_single_user_flair(sub, sub_config, author, swap_count, [])
                except Exception as e:
                        print("Found exception " + str(e) + "\n    Sleeping for 20 seconds...")
                        time.sleep(20)
                        swap.update_single_user_flair(sub, sub_config, author, swap_count, [])
                time.sleep(0.5)
		count += 1
		if count % 25 == 0:
			print("Finished assigning flair for " + str(count) + " users out of " + str(len(users_to_confirmations)) + " users.")

sub_config = config.Config(sub_name)
reddit = praw.Reddit(client_id=sub_config.client_id, client_secret=sub_config.client_secret, user_agent='UserAgent', username=sub_config.bot_username, password=sub_config.bot_password)
sub = reddit.subreddit(sub_config.subreddit_name)
feedback_sub = reddit.subreddit(feedback_sub_name)

#pushshift_ids, authors = GetIdsFromPushshift(sub_name)
#reddit_ids = GetIdsFromReddit(feedback_sub, authors)
#ids = list(set(pushshift_ids + reddit_ids))
ids = ["g0zp3b"]
users_to_confirmations = GetUserCounts(ids, sub_config)
UpdateDatabase(sub_config.subreddit_name, users_to_confirmations)
UpdateFlairs(sub, sub_config, users_to_confirmations)
