import sys
sys.path.insert(0, '.')
import swap
import praw
import Config

sub_config = Config.Config('knife_swap')
message = sub_config.reddit_object.inbox.message('2huyvxb')
print(message.body)

swap.handle_flair_transfer(message, sub_config)
