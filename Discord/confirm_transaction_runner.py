import time
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('subreddit_name', metavar='C', type=str)
args = parser.parse_args()
subreddit_name = args.subreddit_name.lower()

def main():
	while True:
		os.system('python3 Discord/confirm_transaction.py ' + subreddit_name)
		time.sleep(10)

main()
