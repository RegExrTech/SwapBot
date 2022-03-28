import sys
sys.path.insert(0, '.')
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


def main():
	db = requests.get(request_url+"/get-db/").json()
	if args.sub_name.lower() not in db:
		print(args.sub_name.lower() + " was not found as a community in the database.")
	elif args.platform.lower() not in db[args.sub_name.lower()]:
		print(args.platform.lower() + " was not found as a platform in the " + args.sub_name.lower() + " community.")
	elif args.old_username.lower() not in db[args.sub_name.lower()][args.platform.lower()]:
		print(args.old_username.lower() + " was not found in the " + args.platform.lower() + " platform of the " + args.sub_name.lower() + " community. As such, there is nothing to copy over.")
	else:
		swap_text = ",".join(db[args.sub_name.lower()][args.platform.lower()][args.old_username.lower()])
		requests.post(request_url + "/add-batch-swap/", json={'sub_name': args.sub_name.lower(), 'platform': args.platform.lower(), 'user_data': {args.new_username.lower(): swap_text}})
		sub_config, reddit, sub = swap.create_reddit_and_sub(args.sub_name.lower())
		swap.update_flair(reddit.redditor(args.new_username.lower()), None, sub_config)

if __name__ == "__main__":
	main()
