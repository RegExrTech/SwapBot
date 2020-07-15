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
request_url = "http://192.168.0.248:8000"
#requests.post(request_url + "/add-swap/", {'sub_name': args.sub_name, 'username': args.username, 'V': args.swap_text})
json_helper = JsonHelper()
requests.post(request_url + "/add-swap/", {'sub_name': args.sub_name, 'username': args.username.lower(), 'swap_text': args.swap_text.lower()})
