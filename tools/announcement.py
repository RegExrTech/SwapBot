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
	message_content = "Hello Mod Team!\n\nI've gone and added two new features to the Confirmation Bot that I would like to share with you.\n\nThe first feature is the ability for the bot to detect if the tagged account is a real reddit account or not. When the OP tags the bot and their partner in a comment, the often times misspell their partner's name. If the username they tagged does not resolve into a real reddit account, the bot will now inform them as such, prompting them to make a new comment with proper spelling. Of course, this doesn't help in the cases where a type is, in fact, a real redditor, but it'll help cut down on the number of mod mail messages where the OP says 'I tagged by partner and theu replied but nothing happened' due to them misspelling their partner's name. This new feature ALSO can detect if the person they tagged deleted their account, or if the person they tagged had their account suspended by the Reddit Admins. In these cases, the person being tagged obviously will not be able to reply to the bot now informs the OP as such.\n\nThe second feature makes the bot reply to all new comments the first time it sees them, informing the OP that their comment is being tracked and that they'll get credit once their partner replies. Another common mod mail message we would get from users was 'I tagged the bot and nothing happened.' to which the answer is 'You'll get credit once your partner replies.' Considering the bot spells it out every time now, this should reduce the number of messages we get to this effect from users.\n\nHopefully these new features make for a better user experience for your members and easier moderation for the mod team. Please let me know if you have any questions!\n\nBest,\n\nu/RegExr"
	sub.message("Confirmation Bot Announcement", message_content)
