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

	message_content = "Hi Mod Team,\n\nTLDR A Mod Discussion thread is created if the system detects flair boosting on your sub.\n\nThe Swap Bot System now has Flair Boosting Detection enabled by default. Despite the system's robust efforts to curb flair boosting, there will always be people who find a way around it. As such, many of you have been asking for ways to automatically detect when flair boosting is detected within your sub. This was infeasible at the time due to constraints with the database structure, but after roughly 40 hours of coding and changings to the backend architecture to improve RAM efficiency, the feature has finally launched!\n\nWhenever a user is detected as flair boosting in your sub, a notification will be sent to your sub via Mod Mail Mod Discussion. The message will include details as to why the bot thinks this user is boosting their flair. Of course, the bot cannot know for sure if the user is boosting their flair, so please review each message on a case-by-case basis and make the call for yourself if flair boosting is happening or not.\n\nThe bot performs its analysis by looking at **ALL** recent confirmations across **ALL** subs that the system runs on. It counts those recent transactions, checks if it passes the threshold, and sends a message if needed. The two important bits to note here are the `booster_check_count_threshold` and the `booster_check_hours_threshold` variables. The `count` variable is the number of confirmations a user must make before the bot sends a notification, and the `hours` variable is the number of hours that those confirmations must have been done within for the bot to send a notification. For example, if both of those values are set to 3, the bot will send you a notification if someone confirms 3 transactions in under 3 hours.\n\nSome of you might be hesitant about this feature as you have power users who may confirm many transactions in a short amount of time. This is especially true for subreddits that deal in digital goods. This is where the third variable, `booster_check_max_score`, comes into play. `max_score` defines the point at which users are no longer subjected to this check. For example, if the variable is set to 20, no notification will be sent for users with 20 or more confirmed transactions, no matter how quickly they confirm those transactions. Note that this threshold **only** applies to confirmations done on **your** sub. If a user has 1 confirmation on your sub but 100 on another sub, they will *still* be subjected to the booster check when they confirm transactions on your sub.\n\n"
	message_content += "The initial configuration for your sub is as follows:\n\n    booster_check_count_threshold: 3\n\n    booster_check_hours_threshold: 6\n\n    booster_check_max_score: 10\n\nThis means that if a user confirms 3 or more transactions in under 6 hours and their flair score is below 10, a notification will be sent to you via Mod Mail Mod Discussion.\n\nIf you wish to **CHANGE** these values, please visit [your sub's config page](https://www.reddit.com/r/" + sub_config.subreddit_name + "/wiki/swap_bot_config) and modify the relevant values. The bot will automatically update and send you a reply indicating as such.\n\nThis feature has been a long time coming and I'm really excited to get it into your hands. Please reach out to me directly if you have any questions. Otherwise, I hope you enjoy the feature and I hope it makes moderating easier!\n\nBest,\n\nu/RegExr"

	try:
		sub.message(subject="[Swap Bot Update] Flair Booster Detection", message=message_content)
	except:
		print("    Unable to send message to " + subname)
