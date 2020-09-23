#TODO dynamically scrape config directory for subs to run on.
#TODO only go back to the last hour, rather than an arbitrary number of comments (i.e.50)
import praw
import argparse


#parser = argparse.ArgumentParser()
#parser.add_argument('config_file_name', metavar='C', type=str)
#args = parser.parse_args()
#config_fname = 'config/' + args.config_file_name
sub_names = ['mousemarket', 'funkoswap', 'digitalcodesell', 'steelbookswap', 'disneypinswap', 'pkmntcgtrades', 'uvtrade', 'vinylcollectors']
sub_names += ['ecigclassifieds', 'snackexchange', 'bluraysale', 'disneystorekeyswap', 'ygomarketplace', 'comicswap', 'avexchange', 'watchexchange']
for sub_name in sub_names:
	config_fname = 'config/' + sub_name + "-config.txt"

	f = open(config_fname, "r")
	info = f.read().splitlines()
	f.close()

	subreddit_name = info[0].split(":")[1]
	client_id = info[1].split(":")[1]
	client_secret = info[2].split(":")[1]
	bot_username = info[3].split(":")[1]
	bot_password = info[4].split(":")[1]

	reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent='UserAgent', username=bot_username, password=bot_password)

	for message in reddit.inbox.all(limit=50):
		message.mark_unread()
