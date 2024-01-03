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
r = requests.post(request_url + "/remove-user/", {'sub_name': args.sub_name.lower(), 'platform': args.platform.lower(), 'username': args.username.lower()})
print(r.json())
