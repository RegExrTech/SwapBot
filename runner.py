import argparse
import time
import os

parser = argparse.ArgumentParser()
parser.add_argument('config_file_name', metavar='C', type=str)
args = parser.parse_args()
config_fname = args.config_file_name
subreddit_name = config_fname.split("-")[0]

def main():
	while True:
		os.system('python swap.py ' + config_fname)
		time.sleep(30)

time.sleep(3)
ps_output = [x for x in os.popen('ps -ef | grep \&\&\ python\ runner.py\ ' + config_fname).read().splitlines() if 'grep' not in x]
# If the only output we get from grep is the grep itself and this instance of the runner,
# then runner is not currently running so this instance should take over
if len(ps_output) == 1:
	main()
elif len(ps_output) == 3:
	os.system("kill $(ps aux | grep '[p]ython runner.py' | awk '{print $2}')")
