import os

snames = []

for fname in os.listdir("config"):
	sname = "r/" + fname.split("-")[0]
	snames.append(sname)

snames.sort()

f = open("database/subreddits.txt", "w")
f.write("\n".join(snames)+"\n")
f.close()
