import time
import requests
from httplib2 import ServerNotFoundError
from requests.exceptions import ConnectionError, Timeout, HTTPError

import Settings


def post_request(caller, post_data):
	try:
		resp = requests.post(Settings.PATH_TO_SERVER + Settings.RECEIVER, data = post_data)
		if resp.status_code == 200:
			try:
				parsed = resp.json()
				if 'Error' in parsed:
					caller.output.writeErrorLog("Error: 'Error'\n" + str(parsed['Error']))
					return None
				else:
					return parsed['Result']
			except ValueError as e:
				caller.output.writeErrorLog("Error: 'ValueError'\n" + str(resp.content))
				return None
		else:
			resp.raise_for_status()
	except ConnectionError as e:
		caller.output.writeErrorLog("Error: 'ConnectionError'\n" + str(e))
		return None
	except Timeout as e:
		caller.output.writeErrorLog("Error: 'TimeoutError'\n" + str(e))
		return None
	except HTTPError as e:
		caller.output.writeErrorLog("Error: 'HTTPError'\n" + str(e))
		return None


def post_insta_request(caller, post_data, firstTime=False):
	try:
		post_data['username'] = caller.username
		post_data['password'] = caller.password
	except AttributeError as e:
		if firstTime:
			print "AttributeError:\n" + str(e) + "\nwith post data:\n" + str(post_data)
		else:
			caller.output.writeErrorLog("AttributeError:\n" + str(e) + "\nwith post data:\n" + str(post_data))
	try:
		resp = requests.post(Settings.PATH_TO_SERVER_INSTA + Settings.RECEIVER_INSTA, data = post_data)
		if resp.status_code == 200:
			try:
				parsed = resp.json()
				if 'Error' in parsed:
					if firstTime:
						print "Error: 'Error'\n" + str(parsed['Error'])
						print "Dump: \n" + str(parsed['Dump'])
					else:
						caller.output.writeErrorLog("Error: 'Error'\n" + str(parsed['Error']))
						caller.output.writeErrorLog("Dump: \n" + str(parsed['Dump']))
					return None
				else:
					return parsed['Result']
			except ValueError as e:
				if firstTime:
					print "Error: 'ValueError'\n" + str(resp.content)
				else:
					caller.output.writeErrorLog("Error: 'ValueError'\n" + str(resp.content))
				if str(resp.content).find("curl") and str(resp.content).find("28"):
					if firstTime:
						print "Waiting and retring.. "
					else:
						caller.output.writeErrorLog("Waiting and retring.. ")
					time.sleep(10)
					post_insta_request(caller, post_data, firstTime)
				else:
					return None
		else:
			resp.raise_for_status()
	except ConnectionError as e:
		if firstTime:
			print "Error: 'ConnectionError'\n" + str(e)
		else:
			caller.output.writeErrorLog("Error: 'ConnectionError'\n" + str(e))
		return None 
	except Timeout as e:
		if firstTime:
			print "Error: 'TimeoutError'\n" + str(e)
		else:
			caller.output.writeErrorLog("Error: 'TimeoutError'\n" + str(e))
		return None
	except HTTPError as e:
		if firstTime:
			print "Error: 'HTTPError'\n" + str(e)
		else:
			caller.output.writeErrorLog("Error: 'HTTPError'\n" + str(e))
		return None