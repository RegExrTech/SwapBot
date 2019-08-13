import json

FNAME = 'database/swaps-funkoswap.json'
FNAME = 'database/swaps-pkmntcgtrades.json'
FNAME = 'database/swaps-vinylcollectors.json'

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

db = get_db()
new = {}
keys = db.keys()
print(keys[1])
print(len(keys))
int('s')
for key in keys:
	new_key = key.split("/")[1]
	if new_key not in new:
		new[new_key] = db[key]
	else:
		for val in db[key]:
			if val not in new[new_key]:
				new[new_key].append(val)

dump(new)
