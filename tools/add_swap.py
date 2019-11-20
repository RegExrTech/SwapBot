import sys
sys.path.insert(0, '.')
from server import JsonHelper
import requests
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('sub_name', metavar='C', type=str)
parser.add_argument('username', metavar='C', type=str)
#parser.add_argument('swap_text', metavar='C', type=str)
args = parser.parse_args()
request_url = "http://192.168.1.210:8000"
#requests.post(request_url + "/add-swap/", {'sub_name': args.sub_name, 'username': args.username, 'V': args.swap_text})
json_helper = JsonHelper()
db = json_helper.get_db('database/swaps.json')
for swap in db[args.sub_name]['lifeobenreilly']:
	requests.post(request_url + "/add-swap/", {'sub_name': args.sub_name, 'username': args.username, 'swap_text': swap})
