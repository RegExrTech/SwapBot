import requests
import time
import sys
import os
sys.path.insert(0, '.')
import swap
import server

DATA_PATH = 'database/'

request_url = swap.request_url

r = requests.post(request_url + "/dump/")

def load_store_data():
	for fname in os.listdir(DATA_PATH):
		if '.json' not in fname:
			continue
		server.json_helper.get_db(DATA_PATH + fname)

db = load_store_data()
