import sys
import os
sys.path.insert(0, '.')
import swap

subnames = [x.split("-")[0] for x in os.listdir("config/")]
for subname in subnames:
	sub_config, reddit, sub = swap.create_reddit_and_sub(subname)
	message_content = "Hi Mod Team! Quick update for you all on the Mod Assistant Bot.\n\nThe Mod Assistant Bot currently enforces your post-frequency rules (i.e. No more than one post per X days). This normally works perfectly, with the added bonus of ignoring posts that never make it to your sub because they were removed by automod. Any post that is removed by automod is removed for a formatting reason (apart from karma/age requirements, but that doesn't come into play here). Because the removal is just for formatting reasons, usrs are allowed to post again right away and can dismiss the posting frequency rules.\n\nHowever, sometimes automod is backed up and does not take action quickly enough. In these cases, the Mod Assistant Bot will see the post **before** it is removed from the sub. The bot will then record the timestamp in the database and move on. Then, automod will finally get around to removing the post. So the user will make a new post, this time doing so correctly. However, because the mod assistant bot saw their recent post as a valid post despite it being removed by automod, it will remove their most recent post for posting too frequently.\n\nThe change I've added today allows the bot to keep track of previous posts. This way, the bot can look at a post and, before removing it, check it see if the last post it saw was removed by automod. If it was, then it allows the new post to go through, assuming it doesn't still violate the frequency policy.\n\nThanks for taking the time to read this! Please let me know if you have any questions at all.\n\nBest,\n\nu/RegExr"
	sub.message("New Swap Bot Feature - Confirmations in Automod-Authored Posts", message_content)
