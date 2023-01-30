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
db = requests.get(request_url+"/get-db/").json()

sub_config, reddit, sub = swap.create_reddit_and_sub(args.sub_name.lower())

i = 0
for trade in db[args.sub_name.lower()][args.platform.lower()][args.username.lower()]:
	print(str(i) + ") " + trade)
	i += 1

indexes = raw_input("Please select the index you wish to remove:\n>> ")

for index in indexes.split(",")[::-1]:
	requests.post(request_url + "/remove-swap/", {'sub_name': args.sub_name.lower(), 'platform': args.platform.lower(), 'username': args.username.lower(), 'index': index})

if args.platform.lower() == 'reddit':
	swap.update_flair(reddit.redditor(args.username.lower()), None, sub_config)
# TODO: Update this to work for all platforms. Discord should be rolled back as well.
