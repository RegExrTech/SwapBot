import praw
import json

# IDK, I needed this according to stack overflow.
def ascii_encode_dict(data):
        ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
        return dict(map(ascii_encode, pair) for pair in data.items())

# Function to load the swap DB into memory
def get_swap_data(fname):
        with open(fname) as json_data: # open the funko-shop's data
                funko_store_data = json.load(json_data, object_hook=ascii_encode_dict)
        return funko_store_data

config_fname = 'config/digitalcodesell-config.txt'

f = open(config_fname, "r")
info = f.read().splitlines()
f.close()

subreddit_name = info[0].split(":")[1]
if subreddit_name in ['digitalcodesell', 'uvtrade']:
        database_name = 'digitalcodeexchange'
else:
        database_name = subreddit_name
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

reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent='UserAgent', username=bot_username, password=bot_password)
sub = reddit.subreddit(subreddit_name)

def main():
	comment = reddit.comment("faoi0rd")
	author1 = comment.author
	desired_author2_string = "u/tgruch714"
	parent_post = comment
	while parent_post.__class__.__name__ == "Comment":
		parent_post = parent_post.parent()
	print(str(parent_post.author))
        print(not str(author1).lower() == str(parent_post.author).lower() and not "u/"+str(parent_post.author).lower() == desired_author2_string.lower())

main()
