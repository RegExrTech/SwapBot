import json

class JsonHelper:
	def get_db(self, fname, encode_ascii=True):
		with open(fname) as json_data:
			data = json.load(json_data)
		return data

	def dump(self, db, fname, should_shard=False):
		if should_shard:
			shard = 0
			_temp_db = {}
			var_count = 0
			var_max = 100000  # 100,000 should be about 20Mb
			platforms = list(db.keys())
			platforms.sort()
			for platform in platforms:
				if platform not in _temp_db:
					_temp_db[platform] = {}
				users = list(db[platform].keys())
				users.sort()
				for user in users:
					transactions = db[platform][user]
					if "transactions" not in transactions:
						_temp_db[platform][user] = transactions
					elif len(transactions["transactions"]) + var_count < var_max:
						var_count += len(transactions['transactions'])
						_temp_db[platform][user] = transactions
					else:
						_fname = "-".join([fname.split("-")[0], str(shard), fname.split("-")[1]])
						with open(_fname, 'w') as outfile:
							outfile.write(json.dumps(_temp_db, sort_keys=True, indent=4))
						shard += 1
						_temp_db = {platform: {user: transactions}}
						var_count = len(transactions['transactions'])
		else:
			with open(fname, 'w') as outfile:
				outfile.write(json.dumps(db, sort_keys=True, indent=4))

j = JsonHelper()
data = j.get_db('database/digitalcodesell-swaps.json')
j.dump(data, 'database/digitalcodesell-swaps.json', True)
