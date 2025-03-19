import argparse
import time
import os
import random

parser = argparse.ArgumentParser()
parser.add_argument('subreddit_name', metavar='C', type=str)
args = parser.parse_args()
subreddit_name = args.subreddit_name.lower()

def main():
	while True:
		time.sleep(random.randint(30, 120))
		os.system('python3 swap.py ' + subreddit_name)

main()
