import os
import sys
import time
import datetime
import threading
import requests

import Settings


lock = threading.RLock()

sleepCharDefault = 0.02
sleepLineDefault = 0.3
sleepChar = 0.02
sleepLine = 0.3
lastline = ""

PATH_TO_SERVER = Settings.PATH_TO_SERVER


def writeln(res):
	"Write a message with new line symble"
	global lock
	lock.acquire()
	now = datetime.datetime.now()
	nowstr = date2string(now)
	try:
		sys.stdout.write(nowstr + " -> ")
		sys.stdout.flush()
		write(res)
	finally:
		lock.release()


def write(res):
	"Write a message without new line symble"
	global lock, lastline
	lock.acquire()
	lastline = res
	try:
		time.sleep(sleepLine)
		for c in res:
			sys.stdout.write('%s' % c)
			sys.stdout.flush()
			time.sleep(sleepChar)
	finally:
		lock.release()


def clearline():
	"Clear the last line in output"
	global lock, lastline
	lock.acquire()
	try:
		cll = 0
		while cll < len(lastline):
			sys.stdout.write('\b \b')
			cll += 1
	finally:
		sys.stdout.flush()
		lock.release()


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


def checkInputParams():
	pass


def printHello():
	write("""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\
$$$$$$$$$$$$$$$$$$$$$$$$$$   WELCOME SOCIAL BOT   $$$$$$$$$$$$$$$$$$$$$$$$$$\n\
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\n""")


def tryConnectToRemoteServer():
	"Look for the remote server"
	post_data = {"action": "server_alive"}
	resp = requests.post(PATH_TO_SERVER + '/Receiver.php', data = post_data)
	print resp.content


if __name__ == '__main__':
	os.system('clear')
	checkInputParams()
	printHello()

