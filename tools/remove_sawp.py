import sys
sys.path.insert(0, '.')
import requests
import argparse
import swap

parser = argparse.ArgumentParser()
parser.add_argument('sub_name', metavar='C', type=str)
parser.add_argument('platform', metavar='C', type=str)
parser.add_argument('username', metavar='C', type=str)
args = parser.parse_args()
request_url = "http://0.0.0.0:8000"

sub_config, reddit, sub = swap.create_reddit_and_sub(args.sub_name.lower())

db = requests.get(request_url+"/get-sub-db/", data={'sub': sub_config.subreddit_name}).json()

i = 0
if 'legacy_count' in db[args.platform.lower()][args.username.lower()]:
	for _ in range(db[args.platform.lower()][args.username.lower()]['legacy_count']):
		print(str(i) + ") LEGACY TRADE")
		i += 1
for trade in db[args.platform.lower()][args.username.lower()]['transactions']:
	print(str(i) + ") " + trade['partner'] + " - " + trade['post_id'] + " - " + trade['comment_id'])
	i += 1

indexes = input("Please select the index you wish to remove:\n>> ")

cleaned_indexes = []
for index in indexes.split(",")[::-1]:
	if '-' not in index:
		cleaned_indexes.append(int(index))
	else:
		start = int(index.split("-")[0])
		end = int(index.split("-")[1])
		for i in range(start, end+1):
			cleaned_indexes.append(i)
user_data = []
i = 0
if 'legacy_count' in db[args.platform.lower()][args.username.lower()]:
	for _ in range(db[args.platform.lower()][args.username.lower()]['legacy_count']):
		if i in cleaned_indexes:
			user_data.append({'post_id': "LEGACY TRADE"})
		i += 1
for trade in db[args.platform.lower()][args.username.lower()]['transactions']:
	if i in cleaned_indexes:
		user_data.append(trade)
	i += 1

requests.post(request_url + "/remove-swap/", json={'sub_name': args.sub_name.lower(), 'platform': args.platform.lower(), 'username': args.username.lower(), 'transaction_data': user_data})

if args.platform.lower() == 'reddit':
	swap.update_flair(reddit.redditor(args.username.lower()), None, sub_config)
# TODO: Update this to work for all platforms. Discord should be rolled back as well.
