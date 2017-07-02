import requests
from httplib2 import ServerNotFoundError
from requests.exceptions import ConnectionError, Timeout, HTTPError

import Settings


def post_request(caller, post_data):
	try:
		return send_and_check_request(caller, post_data)
	except HTTPError as e:
		caller.writeError("Error: HTTPError\n" + str(e))
		return None


def send_and_check_request(caller, post_data):
	errors = 0
	try:
		resp = requests.post(Settings.PATH_TO_SERVER + Settings.RECEIVER, data = post_data)
		if resp.status_code == 200:
			try:
				parsed = resp.json()
				if 'Error' in parsed:
					caller.writeError("Error:\n" + str(parsed['Error']))
					return None
				else:
					return parsed['Result']
			except ValueError as e:
				caller.writeError("Error: ValueError:\n" + str(resp.content))
				return None
		else:
			resp.raise_for_status()
	except ConnectionError as e:
		caller.writeError("Error: ConnectionError:\n" + str(e))
		errors += 1
		if errors >= caller.MAX_NUM_ERRORS:
			return None
		else:
			time.sleep(5)
			caller.write("Retry to send request!")
			send_and_check_request(caller, post_data)
	except Timeout as e:
		caller.writeError("Error: Timeout Error:\n" + str(e))
		errors += 1
		if errors >= caller.MAX_NUM_ERRORS:
			return None
		else:
			time.sleep(5)
			caller.write("Retry to send request!")
			send_and_check_request(caller, post_data)


def post_insta_request(caller, post_data, firstTime=False):
	try:
		post_data['username'] = caller.username
		post_data['password'] = caller.password
	except AttributeError as e:
		if firstTime:
			print "AttributeError:\n" + str(e)
		else:
			caller.writeError("AttributeError:\n" + str(e))
	try:
		return send_and_check_request_insta(caller, post_data, firstTime)
	except HTTPError as e:
		if firstTime:
			print e
		else:
			caller.writeError(str(e))
		return None


def send_and_check_request_insta(caller, post_data, firstTime=False):
	try:
		resp = requests.post(Settings.PATH_TO_SERVER_INSTA + Settings.RECEIVER_INSTA, data = post_data)
		if resp.status_code == 200:
			try:
				parsed = resp.json()
				if 'Error' in parsed:
					if firstTime:
						print "Error: " + str(parsed['Error'])
					else:
						caller.writeError("Error: " + str(parsed['Error']))
					return None
				else:
					return parsed['Result']
			except ValueError as e:
				if firstTime:
					print "ValueError:\n" + str(resp.content)
				else:
					caller.writeError("ValueError:\n" + str(resp.content))
				return None
		else:
			resp.raise_for_status()
	except ConnectionError as e:
		if firstTime:
			print "ConnectionError:\n" + str(e)
		else:
			caller.writeError("ConnectionError:\n" + str(e))
		return None 
	except Timeout as e:
		if firstTime:
			print "Timeout Error:\n" + str(e)
		else:
			caller.writeError("Timeout Error:\n" + str(e))
		return None