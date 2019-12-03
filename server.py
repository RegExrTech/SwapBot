from flask import Flask, request, render_template, redirect
import json
import time
from collections import defaultdict
from flask import jsonify
from werkzeug.serving import WSGIRequestHandler, _log

#import json_helper

app = Flask(__name__)

class JsonHelper:
	def ascii_encode_dict(self, data):
		ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
		return dict(map(ascii_encode, pair) for pair in data.items())

	def get_db(self, fname):
		with open(fname) as json_data:
			data = json.load(json_data, object_hook=self.ascii_encode_dict)
		return data

	def dump(self, db, fname):
		with open(fname, 'w') as outfile:
			outfile.write(str(db).replace("'", '"').replace('{u"', '{"').replace('[u"', '["').replace(' u"', ' "').encode('ascii','ignore'))

json_helper = JsonHelper()

try:
	swaps_fname = 'database/swaps.json'
	comment_fname = 'database/comments.json'
except: # this happens when we try to start the server sometimes
	pass

# Init DB
swap_data = json_helper.get_db(swaps_fname)
comment_data = json_helper.get_db(comment_fname)

@app.route('/add-comment/', methods=['POST'])
def add_comments():
	"""
	Given a comment ID and sub name, manually adds it to the
	list of comments to check.

	Requested Form Params:
        String sub_name: The name of the current subreddit
	String comment_id: The ID of the comment where the trade took place

	return JSON {}
	"""

	sub_name = request.form["sub_name"]
	comment_id = request.form["comment_id"]

	global comment_data
	if comment_id not in comment_data[sub_name]['active'] and comment_id not in comment_data[sub_name]['archived']:
		comment_data[sub_name]['active'].append(comment_id)
	json_helper.dump(comment_data, comment_fname)
	return jsonify({})


@app.route('/get-comments/', methods=['POST'])
def get_comments():
	"""
	Given a list of new IDs, returns a list of IDs to check.

	Requested Form Params:
	String sub_name: The name of the current subreddit
	String active: Denotes either active or archived ('True' or 'False')
	List(String) ids: List of strings of ids to include with active comments

	Return JSON {'ids': List(String)}
	"""

	sub_name = request.form["sub_name"]
	active = request.form['active'] == 'True'
	ids = request.form['ids'].split(",")
	if not ids[0]:
		ids = []

	global comment_data
	if sub_name not in comment_data:
		comment_data[sub_name] = {'active': [], 'archived': []}

	if active:
		prev_ids = comment_data[sub_name]['active']
	else:
		prev_ids = comment_data[sub_name]['archived']

	for id in ids:
		if id not in prev_ids:
			prev_ids.append(id)
	json_helper.dump(comment_data, comment_fname)
	return jsonify({'ids': prev_ids})

@app.route('/check-comment/', methods=['POST'])
def check_comment():
	"""
	Updates the database for a confirmed trade if it is not a duplicate

	Requested Form Params:
	String sub_name: The name of the current subreddit
	String author1: The first trade partner's name
	String author2: The second trade partner's name
	String post_id: The ID of the post where the trade took place
	String comment_id: The ID of the comment where the trade took place

	Return JSON {'is_duplicate': String, 'flair_count_1': String, 'flair_count_2': String}
	"""

	global swap_data
	global comment_data
	sub_name = request.form["sub_name"]
	if sub_name not in swap_data:
		swap_data[sub_name] = {}
	sub_data = swap_data[sub_name]

	author1 = request.form['author1']
	author2 = request.form['author2']
	post_id = request.form['post_id']
	comment_id = request.form['comment_id']
	real_sub_name = request.form['real_sub_name']

	message = " - https://www.reddit.com/r/" + real_sub_name + "/comments/" + post_id
	if author1 not in sub_data:
		sub_data[author1] = [author2 + message]
	else:
		if author2 + message in sub_data[author1]:
			return jsonify({'is_duplicate': 'True', 'flair_count_1': 0, 'flair_count_2': 0})
		sub_data[author1].append(author2 + message)
	if author2 not in sub_data:
		sub_data[author2] = [author1 + message]
	else:
		if author1 + message in sub_data[author2]:
			return jsonify({'is_duplicate': 'True', 'flair_count_1': 0, 'flair_count_2': 0})
		sub_data[author2].append(author1 + message)
	if comment_id in comment_data[real_sub_name]['active']:
		comment_data[real_sub_name]['active'].remove(comment_id)
	if comment_id in comment_data[real_sub_name]['archived']:
		comment_data[real_sub_name]['archived'].remove(comment_id)
	json_helper.dump(swap_data, swaps_fname)
	json_helper.dump(comment_data, comment_fname)
	return jsonify({'is_duplicate': 'False', 'flair_count_1': len(sub_data[author1]), 'flair_count_2': len(sub_data[author2])})

@app.route('/get-summary/', methods=['POST'])
def get_summary():
	"""
	Given a list of new IDs, returns a list of IDs to check.

	Requested Form Params:
	String sub_name: The name of the current subreddit
	String username: The name of the user to check feedback for

	Return JSON {'data': List(String)}
	"""

	sub_name = request.form["sub_name"]
	if sub_name not in swap_data:
		return jsonify({'data': []})
	sub_data = swap_data[sub_name]
	username = request.form['username']
	if username not in sub_data:
		return jsonify({'data': []})
	return jsonify({'data': sub_data[username]})

@app.route('/archive-comment/', methods=['POST'])
def archive_comment():
	"""
	Removes a comment from the active list and moves it ot the archive list

	Requested Form Parms:
	String sub_name: The name of the current subreddit
	String comment_id: The ID of the comment to archive

	Return JSON {}
	"""

	global comment_data
	sub_name = request.form["sub_name"]
	comment_id = request.form['comment_id']
	if comment_id in comment_data[sub_name]['active']:
		comment_data[sub_name]['active'].remove(comment_id)
	comment_data[sub_name]['archived'].append(comment_id)
	json_helper.dump(comment_data, comment_fname)
	return jsonify({})

@app.route('/remove-comment/', methods=['POST'])
def remove_comment():
	"""
	Removes a comment from being tracked

	Requested Form Params:
	String sub_name: The name of the current subreddit
	String comment_id: The ID of the comment to remove

	Return JSON {}
	"""

	global comment_data
	sub_name = request.form["sub_name"]
	comment_id = request.form['comment_id']
	if comment_id in comment_data[sub_name]['active']:
		comment_data[sub_name]['active'].remove(comment_id)
	if comment_id in comment_data[sub_name]['archived']:
		comment_data[sub_name]['archived'].remove(comment_id)
	json_helper.dump(comment_data, comment_fname)
	return jsonify({})

@app.route('/add-swap/', methods=['POST'])
def add_swap():
	"""
	Adds a swap to a user's profile, given the user and the sub

	Requested Form Params:
        String sub_name: The name of the current subreddit
	String username: The name of the user toadd swaps for
	String swap_text: The text to add for that user

	Return JSON {}
        """

	global swap_data
	sub_name = request.form["sub_name"]
	username = request.form['username']
	swap_text = request.form['swap_text']
	if sub_name not in swap_data:
		swap_data[sub_name] = {}
	if username not in swap_data[sub_name]:
		swap_data[sub_name][username] = []
	swap_data[sub_name][username].append(swap_text)
	json_helper.dump(swap_data, swaps_fname)

@app.route('/dump/', methods=["POST"])
def dump():
	json_helper.dump(swap_data, swaps_fname)
	json_helper.dump(comment_data, comment_fname)

class MyRequestHandler(WSGIRequestHandler):
	# Just like WSGIRequestHandler, but without "code"
	def log_request(self, code='-', size='-'):
		if 200 == code:
			pass
		else:
			self.log('info', '"%s" %s %s', self.requestline, code, size)

if __name__ == "__main__":
	try:
		app.run(host= '0.0.0.0', port=8000, request_handler=MyRequestHandler)

	except:
		pass
