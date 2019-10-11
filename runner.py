import argparse
import datetime
import time
import os

minutes_running_too_long = 20

parser = argparse.ArgumentParser()
parser.add_argument('config_file_name', metavar='C', type=str)
args = parser.parse_args()
config_fname = args.config_file_name
subreddit_name = config_fname.split("-")[0]

def main():
	while True:
		f = open('beingUsed/' + subreddit_name + '.txt', 'w')
		f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
		f.close()
		os.system('python swap.py ' + config_fname)
		time.sleep(30)

f = open('beingUsed/' + subreddit_name + '.txt','r')
beingUsed = f.read().strip()
f.close()

try:
	delta_seconds = (datetime.datetime.now() - datetime.datetime.strptime(beingUsed, '%Y-%m-%d %H:%M:%S.%f')).total_seconds()
except:
	delta_seconds = 9999999999999

if beingUsed == "":
	main()
elif (delta_seconds) > (60*minutes_running_too_long):
	print("=====\nSeconds Delta: " + str(delta_seconds))
	print("Previous Execution started at: " + beingUsed)
	print("Current time is: " + str(datetime.datetime.now()) + "\n=====")
	print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + " Running for too long, killing all and rerunning.")
	main()
