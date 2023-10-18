import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'logger')
import tokens

import json
import requests

TOKENS = tokens.TOKENS
LOG_CHANNEL_ID = '1164211027257339934'

POST = "post"
PUT = "put"
GET = "get"
PATCH = "patch"

def send_request(type, url, headers, data="{}", should_retry=True):
	valid_status_codes = [200, 204]

	if type == POST:
		r = requests.post(url, headers=headers, data=data)
	elif type == PUT:
		r = requests.put(url, headers=headers)
	elif type == GET:
		r = requests.get(url, headers=headers)
	elif type == PATCH:
		r = requests.patch(url, headers=headers, data=data)
	else:
		return

	if r.status_code not in valid_status_codes:
		if len(data) > 6000:
			log("Tried to send a discord request, but len of data was " + str(len(data)) + ". Printing data to logs.")
			print("Discord data too big: \n" + data)
			return r
		try:
			status_data = r.json()
		except Exception as e:
			log("Discord status returned status code " + str(r.status_code) + " and contains no JSON. \n\nRequest URL: " + str(url) + "\n\nRequest Data: " + str(data) + "\n\nStatus text: " + r.text)
			raise e
		# Return early. We don't want to retry or log these failures.
		if 'message' in status_data and 'maximum number of edits to message' in status_data['message'].lower():
			return r
		elif 'retry_after' in status_data and should_retry:
			time.sleep((status_data['retry_after']/1000.0) + 1) # Add some buffer to the sleep
			return send_request(type, url, headers, data, False)
		else:
			print("Discord Failure - status: " + str(r.status_code) + " - text: " + r.text + "\nData: " + str(data))
	return r

def log(message, error=None, trace=''):
	"""
	Given a text message, a potential Python Error, and a potential stack trace, sends nicely formatted text
	to Discord for review by Admins.
	"""
	message = "------------------\n\n<@333321993036365826>\n" + message

	if error:
		message += "\n\nError: " + str(error)
	if trace:
		message += "\n\nStack Trace:\n" + trace
	bot_token = TOKENS['RegExrBot']['token']
	channel_id = LOG_CHANNEL_ID
	headers = {"Authorization":"Bot {}".format(bot_token),
		"User-Agent":"myBotThing (http://some.url, v0.1)",
		"Content-Type":"application/json"}
	baseURL = "https://discordapp.com/api/channels/{}/messages".format(channel_id)
	message = message[:1950]
	send_request(POST, baseURL, headers, json.dumps({"content":message}))

if __name__ == "__main__":
	log('test')
