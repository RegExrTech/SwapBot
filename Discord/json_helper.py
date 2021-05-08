import json

# Function to load the DB into memory
def get_db(fname):
        with open(fname) as json_data: # open the funko-shop's data
                data = json.load(json_data)
        return data

def dump(db, fname):
        with open(fname, 'w') as outfile:  # Write out new data
                outfile.write(str(db).replace("'", '"').replace('{u"', '{"').replace(' u"', ' "').encode('ascii','ignore'))
