import sys
sys.path.insert(0, '.')
from server import JsonHelper
import requests
import swap
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('sub_name', metavar='C', type=str)
parser.add_argument('platform', metavar='C', type=str)
parser.add_argument('old_username', metavar='C', type=str)
parser.add_argument('new_username', metavar='C', type=str)
args = parser.parse_args()

request_url = "http://0.0.0.0:8000"
json_helper = JsonHelper()


def main():
	db = json_helper.get_db('database/swaps.json')
	try:
		swap_text = ",".join(db[args.sub_name.lower()][args.platform.lower()][args.old_username.lower()])
	except:
		print(args.old_username.lower() + " was not found in the " + args.platform.lower() + " platform of the " + args.sub_name.lower() + " community. As such, there is nothing to copy over.")
		return
	requests.post(request_url + "/add-batch-swap/", json={'sub_name': args.sub_name.lower(), 'platform': args.platform.lower(), 'user_data': {args.new_username.lower(): swap_text}})

	sub_config, reddit, sub = swap.create_reddit_and_sub(args.sub_name.lower())
	swap_count = str(swap.get_swap_count(args.new_username.lower(), sub_config.gets_flair_from+[sub_config.database_name], args.platform.lower()))
	swap.update_single_user_flair(sub, sub_config, args.new_username.lower(), swap_count, [], 0)

if __name__ == "__main__":
	main()
