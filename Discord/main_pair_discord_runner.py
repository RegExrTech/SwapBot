import os
import subprocess
import sys
sys.path.insert(0, '.')
import Config

subnames = [x.split(".")[0] for x in os.listdir("config/")]
ps_output = [x for x in os.popen('ps -ef | grep python3\ Discord/pair_discord_runner.py\ ').read().splitlines() if 'grep' not in x]
for subname in subnames:
	if not any([x.endswith(" " + subname) for x in ps_output]):
		raw_data = Config.get_json_data('config/' + subname + ".json")
		if raw_data['discord_config'] and not raw_data['disabled']:
			subprocess.Popen(['python3', 'pair_discord_runner.py', subname])
