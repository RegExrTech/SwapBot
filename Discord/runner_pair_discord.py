import time
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('sub_name', metavar='C', type=str)
args = parser.parse_args()

def main():
	while True:
		os.system('python3 Discord/pair_discord.py ' + args.sub_name)
		time.sleep(10)

main()
