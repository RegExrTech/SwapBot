import praw
import sys
import os
sys.path.insert(0, '.')
import config


subnames = [x.split("-")[0] for x in os.listdir("config/")]
for subname in subnames:
	sub_config = config.Config(subname)
	reddit = praw.Reddit(client_id=sub_config.client_id, client_secret=sub_config.client_secret, user_agent='UserAgent', username=sub_config.bot_username, password=sub_config.bot_password)
	sub = reddit.subreddit(sub_config.subreddit_name)
	message_content = "Hello mod team!\n\nJust a quick note. I recently made a code change that accidentally disabled 'flair titles' for user flairs. This is the bit of fun text that goes after a user's flair, not the actual count itself. As such, any user who confirmed a transaction with the bot while the flair title feature was disabled is missing it from their flair. I've since fixed the issue so their flair will go back to normal the next time they confirm a transaction, but I just wanted to make everyone aware in case users send messages asking what happened to their title.\n\nSorry for the inconveience but thank you for your help!"
	sub.message("Swab Bot Announcement", message_content)
