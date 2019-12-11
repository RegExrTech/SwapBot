import time
import urllib
import requests
import re
import json
import praw
import time
import datetime

# IDK, I needed this according to stack overflow.
def ascii_encode_dict(data):
        ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
        return dict(map(ascii_encode, pair) for pair in data.items())

# Function to load the swap DB into memory
def get_swap_data(fname):
        with open(fname) as json_data: # open the funko-shop's data
                funko_store_data = json.load(json_data, object_hook=ascii_encode_dict)
        return funko_store_data

request_url = "http://192.168.1.210:8000"
debug = False

sub_name = "pkmntcgtrades"
sub_name = "vinylcollectors"
sub_name = 'uvtrade'
sub_name = 'disneypinswap'
sub_name = 'mousemarket'
sub_name = 'digitalcodeexchange'
sub_name = 'ecigclassifieds'
sub_name = 'digitalcodesell'
f = open("config/" + sub_name + "-config.txt", "r")
info = f.read().splitlines()
f.close()

subreddit_name = info[0].split(":")[1]
client_id = info[1].split(":")[1]
client_secret = info[2].split(":")[1]
bot_username = info[3].split(":")[1]
bot_password = info[4].split(":")[1]
if info[5].split(":")[1]:
        flair_word = " " + info[5].split(":")[1]
else:
        flair_word = " Swaps"
if info[6].split(":")[1]:
        mod_flair_word = info[6].split(":")[1] + " "
else:
        mod_flair_word = ""
if info[7].split(":")[1]:
        flair_templates = get_swap_data('templates/'+subreddit_name+'.json')
else:
        flair_templates = False
if info[8].split(":")[1]:
        confirmation_text = info[8].split(":")[1]
else:
        confirmation_text = "Added"
if info[9].split(":")[1]:
        flair_threshold = int(info[9].split(":")[1])
else:
        flair_threshold = 0
if info[10].split(":")[1]:
        mod_flair_template = info[10].split(":")[1]
else:
        mod_flair_template = ""
if info[11].split(":")[1]:
        titles = get_swap_data('titles/'+subreddit_name+'.json')
else:
        titles = False

FNAME_comments = 'database/comments.json'
FNAME_swaps = 'database/swaps.json'

def add_legacy_from_flair_css(reddit, sub):
	for flair in sub.flair(limit=None):
		user = str(flair['user'])
		try:
			count = int(flair['flair_css_class'])
		except:
			count = 0
		for i in range(count):
			requests.post(request_url + "/add-swap/", {'sub_name': subreddit_name, 'username': user, 'swap_text': "LEGACY TRADE"})
		print(user + " - " + str(count))

def transfer_credit(reddit, sub, old_name, new_name):
	old_name = old_name.lower()
	new_name = new_name.lower()
	old_info = requests.post(request_url + "/get-summary/", {'sub_name': subreddit_name, 'username': old_name}).json()
	for trade in old_info['data']:
		requests.post(request_url + "/add-swap/", {'sub_name': subreddit_name, 'username': new_name, 'swap_text': trade})

reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent='UserAgent', username=bot_username, password=bot_password)
sub = reddit.subreddit(subreddit_name)

#add_legacy_from_flair_css(reddit, sub)
transfer_credit(reddit, sub, 'quizkidddonniesmith', 'Particular-Camel')
