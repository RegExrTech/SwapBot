import sys
sys.path.insert(0, '.')
from server import JsonHelper
import requests
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('sub_name', metavar='C', type=str)
parser.add_argument('username', metavar='C', type=str)
parser.add_argument('swap_text', metavar='C', type=str)
args = parser.parse_args()
request_url = "http://192.168.0.155:8000"
json_helper = JsonHelper()
requests.post(request_url + "/add-batch-swap/", json={'sub_name': args.sub_name.lower(), 'user_data': {"username": args.username.lower(), 'swap_text': ",".join(["LEGACY TRADE" for i in range(int(args.swap_text.lower()))])}})
