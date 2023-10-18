import os

snames = []

f = open("database/subreddits.txt", "r"))
old_content = f.read()
f.close()

for fname in os.listdir("config"):
	sname = "r/" + fname.split("-")[0]
	snames.append(sname)

snames.sort()
new_content = "\n".join(snames)+"\n"

if new_content.strip() != old_content.strip():
	f = open("database/subreddits.txt", "w")
	f.write(new_content)
	f.close()

