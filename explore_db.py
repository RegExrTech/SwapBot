from collections import defaultdict
import json

FNAME = 'database/swaps.json'
#FNAME = 'database/comments.json'

# required function for getting ASCII from json load
def ascii_encode_dict(data):
        ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
        return dict(map(ascii_encode, pair) for pair in data.items())

# Function to load the DB into memory
def get_db():
        with open(FNAME) as json_data: # open the funko-shop's data
                funko_store_data = json.load(json_data, object_hook=ascii_encode_dict)
        return funko_store_data

def dump(swap_data):
        with open(FNAME, 'w') as outfile:  # Write out new data
                outfile.write(str(json.dumps(swap_data))
                        .replace("'", '"')
                        .replace(', u"', ', "')
                        .replace('[u"', '["')
                        .replace('{u"', '{"')
                        .encode('ascii','ignore'))

def print_sorted_dict(d):
	sorted_d = defaultdict(lambda: [])
	for key in d:
		value = d[key]
		sorted_d[value].append(key)
	keys = sorted_d.keys()
	keys.sort()
	for key in keys:
		for value in sorted_d[key]:
			print(str(key) + " - " + str(value))

def get_common_users(db):
	all_users = {}
	users = []
	for sub in db:
		if sub in ['digitalcodesell', 'uvtrade']:
			continue
		for user in db[sub]:
			all_users[user] = ''
			for sub2 in db:
				if sub2 in ['digitalcodesell', 'uvtrade']:
					continue
				if sub2 == sub:
					continue
				if user in db[sub2]:
					users.append(user)
	users = list(set(users))

	for user in users:
		print("=== " + user + " ===")
		for sub in db:
			if sub in ['digitalcodesell', 'uvtrade']:
				continue
			if user in db[sub]:
				print("  " + sub + " - " + str(len(db[sub][user])))
	print("Total cross-sub users: " + str(len(users)))
	print("Total Users: " + str(len(all_users.keys())))

def get_highest(db):
	for sub in db:
		highest = 0
		h_user = ""
		for user in db[sub]:
			if len(db[sub][user]) > highest and not user == 'none':
				highest = len(db[sub][user])
				h_user = user
		print(sub + " - " + h_user + " - " + str(highest))

def print_user_in_sub(db, sub, user):
	print("=== " + sub + " ===")
	print("    " + "\n    ".join(db[sub][user]))

def count_partners(db, sub, user):
	d = defaultdict(lambda:0)
	for trade in db[sub][user]:
		partner = trade.split(" - ")[0]
		d[partner] += 1
	return d

db = get_db()

#db = db['ecigclassifieds']
#db = db['digitalcodesell']
#get_common_users(db)
#get_highest(db)
del(db['uvtrade'])
del(db['digitalcodesell'])

print(db['mousemarket']['yaloxcsgo'])

'''usernames = ['Loverblue79']
usernames = ['AltonKastle', 'carib2g']
usernames = ['totlivucl', 'neidolan']
partners = []
for username in usernames:
	username = username.lower()
	for sub in db:
		if username in db[sub]:
			print_user_in_sub(db, sub, username)
			partners.append(count_partners(db, sub, username))
			print_sorted_dict(partners[-1])
for partner in partners[0]:
	if partner in partners[1]:
		print(partner)
'''

'''d = {}
pairs = defaultdict(lambda:0)
usernames = db['digitalcodeexchange'].keys()
for username in usernames:
	d[username] = count_partners(db, 'digitalcodeexchange', username)
for i in range(len(usernames)):
	if i == len(usernames)-1:
		continue
	for j in range(i+1, len(usernames)):
		for partner in d[usernames[i]]:
			if partner in d[usernames[j]]:
				pairs[usernames[i] + " + " + usernames[j]] += 1
for pair in pairs.keys():
	if pairs[pair] >= 10:
		print(pair + " - " + str(pairs[pair]))
'''
#dump(db)

