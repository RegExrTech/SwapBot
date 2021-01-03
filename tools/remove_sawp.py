import sys
sys.path.insert(0, '.')
from server import JsonHelper
import requests
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('sub_name', metavar='C', type=str)
parser.add_argument('username', metavar='C', type=str)
args = parser.parse_args()
request_url = "http://0.0.0.0:8000"
json_helper = JsonHelper()
db = json_helper.get_db('database/swaps.json')

i = 0
for trade in db[args.sub_name.lower()][args.username.lower()]:
	print(str(i) + ") " + trade)
	i += 1

indexes = raw_input("Please select the index you wish to remove:\n>> ")

for index in indexes.split(",")[::-1]:
	requests.post(request_url + "/remove-swap/", {'sub_name': args.sub_name.lower(), 'username': args.username.lower(), 'index': index})
