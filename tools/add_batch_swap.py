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
requests.post(request_url + "/add-batch-swap/", json={'sub_name': args.sub_name.lower(), 'platform': args.platform.lower(), 'user_data': {args.username.lower(): ",".join(["LEGACY TRADE" for i in range(args.swap_count)])}})
sub_config, reddit, sub = swap.create_reddit_and_sub(args.sub_name.lower())
swap.update_flair(reddit.redditor(args.username.lower()), None, sub_config)
