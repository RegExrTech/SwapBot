import os
import sys
sys.path.insert(0, '.')
import Config

snames = []

f = open("database/subreddits.txt", "r")
old_content = f.read()
f.close()

for fname in os.listdir("config"):
	raw_data = Config.get_json_data('config/' + fname)
	if raw_data['bot_username'] and not raw_data['disabled']:
		snames.append("r/" + fname.split(".")[0])

snames.sort()
new_content = "\n".join(snames)+"\n"

if new_content.strip() != old_content.strip():
	f = open("database/subreddits.txt", "w")
	f.write(new_content)
	f.close()

