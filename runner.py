import argparse
import time
import os

parser = argparse.ArgumentParser()
parser.add_argument('subreddit_name', metavar='C', type=str)
args = parser.parse_args()
subreddit_name = args.subreddit_name.lower()

def main():
	while True:
		os.system('python3 swap.py ' + subreddit_name)
		time.sleep(30)

time.sleep(3)
ps_output = [x for x in os.popen('ps -ef | grep \&\&\ python3\ runner.py\ ' + subreddit_name + "\ ").read().splitlines() if 'grep' not in x]
# If the only output we get from grep is the grep itself and this instance of the runner,
# then runner is not currently running so this instance should take over
if len(ps_output) == 1:
	main()
#elif len(ps_output) == 3:
#	os.system("kill $(ps aux | grep '[p]ython runner.py' | awk '{print $2}')")
