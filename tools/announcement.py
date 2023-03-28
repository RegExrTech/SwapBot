import sys
import os
sys.path.insert(0, '.')
import swap

subnames = [x.split(".")[0] for x in os.listdir("config/")]
for subname in subnames:
	print(subname)
	sub_config, reddit, sub = swap.create_reddit_and_sub(subname)
	message_content = "Hi Mod Team!\n\nTLDR You can now control the bot's behavior through a configuration wiki page.\n\nThe Swap Bot System has grown considerably, running against more than 50 communities! As such, it has become unscalable for me to make small changes to each bot here and there. As such, I've devised a new method for giving moderators more direct control over the behavior of their bot.\n\nCheck out https://www.reddit.com/r/" + subname + "/wiki/swap_bot_config/ to see your bot's configuration. The user guide to that configuration page will always be linked at the top, but you can also find it [here](https://redd.it/yixgoa). This change is especially helpful for folks who utilize the username 'black list' feature to prevent user flairs from updating. You can now override a user's flair and add them to this list to prevent the bot from clobbering their flair when they confirm their next transaction.\n\nI'll keep an eye on this thread so please reply if you have any questions or feedback! Hopefully this is helpful change that not only puts some of the control back in your hands but also speeds up your ability to get things done as I am no longer the single point of contact for making changes to the bot configuration.\n\nBest,\n\nu/RegExr\n\nP.S. The wiki pages are only viewable by moderators so no need to worry about random community members stumbling upon this."
	try:
		sub.message("Swap Bot Update - Configure Your Bot via Wiki Page!", message_content)
	except:
		print("Unable to send message to " + subname)
