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
	message_content = "Hello mod team!\n\nJust a quick message for everyone. Previously, the swap bot did not work if the user copy/pasted the bot's name. This was because reddit would treat this as a hyper link rather than a traditional tag. The bot only triggered off tags, so these hyper links did nothing. As such, your sub had automod configured to warn users if they copy/pasted the bot's name and told them how to fix it.\n\nWith the newest update to the bot, it now no longer matters if the bot's name was copy/pasted or not. The bot now looks at notifications for tags AND at the most recent 20 comments on the sub for mentions of its name. This feed also includes 'edited' comments as a 'new' comment, so the bot will even be able to detect if someone edited a comment and included the bot's name as a hyper link. As such, I've removed all of the automod config that warns users against copying and pasting the bot's name.\n\nThis should be a huge quality of life improvement for the users of your sub. Not only does this fix the copy/paste issue, but it also fixes the issue where reddit would sometimes not give the bot a notification for a tag, despite the tag being done properly.\n\nThanks again for all the hard work you put in as a team. Let me know if you have any questions!\n\nBest,\n\nu/RegExr\n\nP.S. I'll be using this format to send important updates about the Swap Bot in the future. Let me know if you have any suggestions for improving how I send these messages!"
	sub.message("Swab Bot Announcement", message_content)
