import sys
import os
sys.path.insert(0, '.')
import swap

subnames = [x.split("-")[0] for x in os.listdir("config/")]
for subname in subnames:
	sub_config, reddit, sub = swap.create_reddit_and_sub(subname)
	message_content = "Hi Mod Team! I've made a super small but interesting change tho the swap bot that I wanted to share with you all.\n\nWhen the bot replies to a users comment to 'confirm' the transaction, the bot will now *also* leave a note stating exactly what each user's flair was changed to.\n\nThis is an improvement to the user experience as now BOTH parties will get a notification when the bot updates their flair, as oppposed to just the person who the bot is replying to.\n\nThis is also an improvement for moderators as well. Mods can now click on the bot's profile, filter by comments, and easily see who is transacting with who and what their flairs are at a glance. This makes it easy for mods to quickly profile what is happening on their sub and make sure everything is above water.\n\n [Here is an example](https://imgur.com/a/NxuZFf1) of this new feature in action.\n\nThanks for taking the time to read this! Please let me know if you have any questions at all.\n\nBest,\n\nu/RegExr"
	sub.message("New Swap Bot Feature - Flair Change Logging", message_content)
