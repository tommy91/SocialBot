import sys
import time
import logging
import datetime
import threading

from Utils import *
import Settings

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG, datefmt='%m/%d/%y %H:%M:%S', filename=Settings.LOGFILE_PATH)


class Output:

	sleepCharDefault = 0.02
	sleepLineDefault = 0.3
	lastline = ""
	startSimble = "-> "
	canWrite = True


	def __init__(self, sleepChar = None, sleepLine = None):
		if sleepChar != None:
			self.sleepChar = sleepChar
		else:
			self.sleepChar = self.sleepCharDefault
		if sleepLine != None:
			self.sleepLine = sleepLine
		else:
			self.sleepLine = self.sleepLineDefault
		self.lock = threading.RLock()


	def writeln(self, res, force = False):
		"Write a message with new line symble"
		if (not force) and (not self.canWrite):
			return
		self.lock.acquire()
		# now = datetime.datetime.now()
		# nowstr = date2string(now)
		try:
			# sys.stdout.write(nowstr + self.startSimble)
			# sys.stdout.flush()
			self.write(res, force)
		finally:
			self.lock.release()


	def write(self, res, force = False):
		"Write a message without new line symble"
		if (not force) and (not self.canWrite):
			return
		self.lock.acquire()
		self.lastline = res
		try:
			# time.sleep(self.sleepLine)
			logging.info(res)
			# for c in res:
			# 	sys.stdout.write('%s' % c)
			# 	sys.stdout.flush()
			# 	time.sleep(self.sleepChar)

		finally:
			self.lock.release()


	def clearline(self):
		"Clear the last line in output"
		self.lock.acquire()
		try:
			cll = 0
			while cll < len(self.lastline):
				sys.stdout.write('\b \b')
				cll += 1
		finally:
			sys.stdout.flush()
			self.lock.release()


	def changeSpeed(self, entry):
		e = entry.split()
		l = len(entry.split())
		if (l > 1) and (l < 6):
			c = 1
			while c < l:
				if e[c] == "-c":
					c = c + 1
					if e[c] == "default":
						self.sleepChar = self.sleepCharDefault
					else:
						try:
							self.sleepChar = float(e[c])
						except ValueError, msg:
							self.write("   Error: " + str(msg) + "\n",True)
							break
					self.write("New speed char: " + str(self.sleepChar) + "\n",True)
					c = c + 1
				elif e[c] == "-l":
					c = c + 1
					if e[c] == "default":
						self.sleepLine = self.sleepLineDefault
					else:
						try:
							self.sleepLine = float(e[c])
						except ValueError, msg:
							self.write("   Error: " + str(msg) + "\n",True)
							break
					self.write("New speed line: " + str(self.sleepLine) + "\n",True)
					c = c + 1 
				else:
					self.write("Error: expecting '-c' or '-l' at " + str(c) + " position!\n",True)
					break
		elif l >= 6:
			self.write("Error: too many arguments!\n",True)
		else:
			self.write("Current speeds:\n   char: " + str(self.sleepChar) + "\n   line: " + str(self.sleepLine) + "\n",True)
			self.write("For modify this values enter:\n",True)
			self.write("   changeSpeed -c 'float_value/default' -l 'float_value/default'\n",True)

