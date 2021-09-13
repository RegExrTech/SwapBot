import sys
import os
sys.path.insert(0, '.')
import swap

subnames = [x.split("-")[0] for x in os.listdir("config/")]
for subname in subnames:
	sub_config, reddit, sub = swap.create_reddit_and_sub(subname)
	message_content = "Hello Mod Team!\n\nI come to you today with a new feature for the swap bot. This new feature is called **Post Age Threshold**. This feature is designed to increase the integrity of the feedback system. It is an optional threshold for the amount of time that must have passed before a transaction can be confirmed on a post. So, for example, if I sell a widget on r/WidgetSwap, I have to wait for payment, pack the item, ship it, then wait for the item to arrive. Obviously this cannot happen in a day's time, so if I tried to invoke the bot and get credit for this transaction right away, I would be doing so incorrectly as confirmations must happen **after** *both* sides have received their end of the deal.\n\nI know that some subs deal in digital transactions and other subs allow users to make posts specifically for confirming transactions that have occured elsewhere, like in a WTB post made by automod, so this feature will not be helpful to everyone.\n\nHowever, if you feel that setting a threshold for the amount of time that must pass before users can confirm transactions on a post would be helpful to your community, please reply to this message with your desired threshold! Thresholds are stored as days, but any amount of time is acceptable (for example, 12 hours would be represented as 0.5 days). If no threshold is selected, the default will be 0 days aka no change to the way the system currently works.\n\nHopefully this new feature is helpful to you and your community! Please let me know if you have any feedback.\n\nBest,\n\nu/RegExr"
	sub.message("New Swap Bot Feature - Post Age Threshold", message_content)
