import requests
from httplib2 import ServerNotFoundError
from requests.exceptions import ConnectionError, Timeout, HTTPError

import Settings


def seconds2timeStr(secs):
	seconds = secs % 60
	minutes = (secs / 60) % 60
	hours = (secs / (60*60)) % 24
	days = (secs / (60*60*24))
	time = []
	if days > 1:
		time.append(str(days) + " days")
	elif days == 1:
		time.append("1 day")
	if hours > 1:
		time.append(str(hours) + " hours")
	elif hours == 1:
		time.append("1 hour")
	if minutes > 1:
		time.append(str(minutes) + " minutes")
	elif minutes == 1:
		time.append("1 minute")
	if seconds > 1:
		time.append(str(seconds) + " seconds")
	elif seconds == 1:
		time.append("1 second")
	if time != []:
		last = time.pop()
		if time != []:
			return ', '.join(time) + " and " + last
		else:
			return last


def date2string(d):
		day = date2str(d.day)
		month = date2str(d.month)
		year = date2str(d.year)
		hour = date2str(d.hour)
		minute = date2str(d.minute)
		second = date2str(d.second)
		return (str(hour) + ":" + str(minute) + ":" + str(second) + " " + str(day) + "/" + str(month))


def date2str(objDate):
	s = str(objDate)
	if len(s) == 1:
		s = "0" + s
	return s


def tags2list(tags):
	tagsList = []
	for tag in tags:
		tagsList.append(tag['Name'])
	return tagsList


def blogs2list(other_accounts):
	oaList = []
	for oa in other_accounts:
		oaList.append(oa['Name'])
	return oaList


def post_request(post_data):
	try:
		return send_and_check_request(post_data)
	except HTTPError as e:
		print e
		return None


def send_and_check_request(post_data):
	try:
		resp = requests.post(Settings.PATH_TO_SERVER + Settings.RECEIVER, data = post_data)
		if resp.status_code == 200:
			try:
				parsed = resp.json()
				if 'Error' in parsed:
					print "Errore: " + str(parsed['Error'])
					return None
				else:
					return parsed['Result']
			except ValueError as e:
				print "Errore:"
				print resp.content
				return None
		else:
			resp.raise_for_status()
	except ConnectionError as e:
		print "Errore:"
		print e
		return None 
	except Timeout as e:
		print "Errore:"
		print e
		return None