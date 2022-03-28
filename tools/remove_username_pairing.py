import sys
sys.path.insert(0, '.')
import requests
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('platform1', metavar='C', type=str)
parser.add_argument('username1', metavar='C', type=str)
parser.add_argument('platform2', metavar='C', type=str)
parser.add_argument('username2', metavar='C', type=str)
args = parser.parse_args()
request_url = "http://0.0.0.0:8000"
removed = requests.post(request_url + "/remove-username-pairing/", data={'platform1': args.platform1.lower(), 'platform2': args.platform2.lower(), 'username1': args.username1.lower(), 'username2': args.username2.lower()}).json()
for platform in removed:
	print("Removed " + removed[platform] + " from " + platform)
