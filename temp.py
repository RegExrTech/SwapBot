from collections import defaultdict
import time
import sys
sys.path.insert(0, '../FunkoAlertingService/utils')
import json_helper

FNAME = 'database/swaps-funkoswap.json'
blog_fname = 'database/blog_posts.json'

def print_store(db, store):
	for url in db[store]:
		print_specific_item(db, store, url)

def print_item(db, name):
	for store in db:
		for url in db[store]:
			if name in url:
				print_specific_item(db, store, url)

def print_item_by_name(db, name):
	for store in db:
		for url in db[store]:
			if name in db[store][url]['name'].lower():
				print_specific_item(db, store, url)

def print_specific_item(db, store, url):
	print("\n" + url)
	for field in db[store][url]:
		print("    " + field + (" "*(18-len(field))) + str(db[store][url][field]))

def print_most_recent_item_from_store(db, store):
	max_time_seen = 0
	item = None
	for url in db[store]:
		time_seen = db[store][url]['last_time_seen']
		if time_seen > max_time_seen:
			max_time_seen = time_seen
			item = db[store][url]
	print(item)

def remove_store(db, store):
	new_db = {}
	for store in db:
		if store == 'target':
			print("Removing Target...")
			continue
		new_db[store] = db[store]
	json_helper.dump(new_db, FNAME)

def get_closeness(blog_url, name):
	stop_words = ['pop', 'funko', 'exclusive']
	score = 0
	blog_words = [x.lower() for x in blog_url.split("-")]
	for word in stop_words:
		if word in blog_words:
			blog_words.remove(word)
	name_words = [x.lower() for x in name.split(" ")]
	for word in name_words:
		if word in blog_words:
			score += 1
	return score

def print_most_recent_item_all_stores(db):
	for store in db.keys():
	        max_time_seen = 0
	        item = None
	        for url in db[store]:
	                time_seen = db[store][url]['last_time_seen']
        	        if time_seen > max_time_seen:
                	        max_time_seen = time_seen
                        	item = db[store][url]
		try:
		        print(store + " - " + str(time.strftime('%m/%d/%Y %H:%M:%S',  time.gmtime(item['last_time_seen']))))
		except:
			print(store)


db = json_helper.get_db(FNAME)

#print_item(db, 'movie-moment')
#print_store(db, 'fugitivetoys')
#print_item_by_name(db, 'molten man')
#print_most_recent_item_from_store(db, "fye")
#print_specific_item(db, "amazon", "b07pgl8mrq")
#print_most_recent_item_all_stores(db)

#db['fugitivetoys']['https://www.fugitivetoys.com/collections/fugitive-toys/products/preorder-rock-the-vote-pop-vinyl-snoopy-3-pack-nycc-exclusive']['num_times_posted'] = 1

#json_helper.dump(db, FNAME)
#print(db.keys())
print(db["bruinsmashabs"])
