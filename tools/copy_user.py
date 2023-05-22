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
	sub_name = args.sub_name.lower()
	platform = args.platform.lower()
	old_username = args.old_username.lower()
	new_username = args.new_username.lower()
	if sub_name == 'all':
		subs = [sub_name for sub_name in db if 'reddit' in db[sub_name] and old_username in db[sub_name]['reddit']]
	else:
		subs = [sub_name]
	for sub_name in subs:
		if sub_name not in db:
			print(sub_name + " was not found as a community in the database.")
		elif platform not in db[sub_name]:
			print(platform + " was not found as a platform in the " + sub_name + " community.")
		elif old_username not in db[sub_name][platform]:
			print(old_username + " was not found in the " + platform + " platform of the " + sub_name + " community. As such, there is nothing to copy over.")
		else:
			swap_text = ",".join(db[sub_name][platform][old_username])
			requests.post(request_url + "/add-batch-swap/", json={'sub_name': sub_name, 'platform': platform, 'user_data': {new_username: swap_text}})
			sub_config, reddit, sub = swap.create_reddit_and_sub(sub_name)
			swap.update_flair(reddit.redditor(new_username), None, sub_config)

if __name__ == "__main__":
	main()
