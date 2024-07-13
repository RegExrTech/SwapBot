import sys
import os
sys.path.insert(0, '.')
import swap

subnames = [x.split(".")[0] for x in os.listdir("config/")]
for subname in subnames:
	print(subname)
	sub_config, reddit, sub = swap.create_reddit_and_sub(subname)
	if sub_config.disabled or not sub_config.bot_username:
		print("    Skipping...")
		continue

	message_content = "Hi Mod Team,\n\nI'm very excited to share today's update with you all. As many of you may know, you can send a DM to the bot with a username in the message to get a detailed look at that user's transaction history. However, this was fairly slow and not a great interface.\n\nNow, this same data is located directly within the wiki pages of your sub. As users confirm transactions, their wiki page is updated accordingly, so it's always up to date with the most recent info. The wiki pages are unlisted and can only be edited by mods but are viewable by everyone.\n\nFor example, if you wanted to see my transaction history on r/PKMNTCGTrades, you could navigate to https://www.reddit.com/r/PKMNTCGTrades/wiki/confirmations/regexr. Inside, you'll see a link to the thread, along with who I completed the transaction with and how many confirmations *they* have.\n\nAdditionally, if you get flair from other subreddits, you'll see any confirmations a user has done in those subs in their wiki page as well.\n\nIf you're interested in seeing an overview across all subs for a user, you can navigate to r/RegExrSwapBot to see this data. For example, you can see all of my transactions at https://www.reddit.com/r/RegExrSwapBot/wiki/confirmations/regexr. From there, you can see how many confirmations I have in each sub and use the links to get a more detailed breakdown of those transactions.\n\nYou can start using this right away by replacing links in automod messages to point people towards these wiki pages rather than having them send a DM to the bot.\n\nFinally, this information now appears on the Universal Scammer List website for **NON-BANNED** accounts. So, for example, you can [look me up on the USL](https://www.universalscammerlist.com/?username=regexr) and see the same info you'd see if you looked at my overview wiki page. This is a nice benefit for folks who use the USL search often to get some more info about their partners before they complete a transaction.\n\nPlease let me know if you have any questions about this! Looking forward to seeing how you incorporate it into your subs!\n\nBest,\n\nu/RegExr\n\nP.S. Huge shout out to u/zeroair for this idea!"

	try:
		sub.message(subject="[Swap Bot Update] Confirmations in Wiki Pages", message=message_content)
	except:
		print("    Unable to send message to " + subname)
