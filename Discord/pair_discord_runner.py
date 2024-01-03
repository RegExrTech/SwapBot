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

time.sleep(3)
ps_output = [x for x in os.popen('ps -ef | grep \&\&\ python3\ Discord/pair_discord_runner.py\ ' + args.sub_name).read().splitlines() if 'grep' not in x]
# If the only output we get from grep is the grep itself and this instance of the runner,
# then runner is not currently running so this instance should take over
if len(ps_output) == 1:
	main()
elif len(ps_output) == 3:
	os.system("kill $(ps aux | grep '[p]ython3 Discord/pair_discord_runner.py' | awk '{print $2}')")
