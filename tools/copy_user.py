import sys
sys.path.insert(0, '.')
from server import JsonHelper
import requests
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('sub_name', metavar='C', type=str)
parser.add_argument('old_username', metavar='C', type=str)
parser.add_argument('new_username', metavar='C', type=str)
args = parser.parse_args()
request_url = "http://192.168.0.248:8000"
json_helper = JsonHelper()
db = json_helper.get_db('database/swaps.json')
for swap in db[args.sub_name.lower()][args.old_username.lower()]:
	requests.post(request_url + "/add-swap/", {'sub_name': args.sub_name.lower(), 'username': args.new_username.lower(), 'swap_text': swap})
