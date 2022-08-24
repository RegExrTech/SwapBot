import sys
sys.path.insert(0, '.')
import requests
import argparse
import swap

parser = argparse.ArgumentParser()
parser.add_argument('sub_name', metavar='C', type=str)
parser.add_argument('platform', metavar='C', type=str)
parser.add_argument('username', metavar='C', type=str)
parser.add_argument('swap_count', metavar='C', type=int)
args = parser.parse_args()
request_url = "http://0.0.0.0:8000"
user_data = ",".join(["LEGACY TRADE" for i in range(args.swap_count)])
username = args.username.lower()
requests.post(request_url + "/add-batch-swap/", json={'sub_name': args.sub_name.lower(), 'platform': args.platform.lower(), 'user_data': {username: user_data}})
sub_config, reddit, sub = swap.create_reddit_and_sub(args.sub_name.lower())
swap.update_flair(reddit.redditor(username), None, sub_config)
