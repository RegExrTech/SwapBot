import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('sub_name', metavar='C', type=str)
parser.add_argument('platform', metavar='C', type=str)
parser.add_argument('comment_id', metavar='C', type=str)
args = parser.parse_args()
request_url = "http://0.0.0.0:8000"
requests.post(request_url + "/add-comment/", {'sub_name': args.sub_name.lower(), 'platform': args.platform.lower(), 'comment_id': args.comment_id})
