import json

FNAME = 'database/swaps-funkoswap.json'
FNAME = 'database/swaps-pkmntcgtrades.json'
FNAME = 'database/swaps-vinylcollectors.json'
FNAME = 'database/swaps-digitalcodesell.json'
FNAME = "database/swaps-uvtrade.json"

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
print(db.keys())
name = "nelson914"
print(db[name.lower()])
print(len(db[name.lower()]))
#dump(db)
