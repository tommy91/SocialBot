import datetime
import threading

import Utils


class Output:

	lastline = ""
	startSimble = "-> "
	canWrite = True


	def __init__(self):
		print "Creating new Output object.."
		self.lock = threading.RLock()
		print "Output object created."


	def writeln(self, res, force = False):
	    "Write a message with new line symble"
	    if (not force) and (not self.canWrite):
	        return
	    self.lock.acquire()
	    now = datetime.datetime.now()
	    nowstr = self.date2string(now)
	    try:
	        sys.stdout.write(nowstr + self.startSimble)
	        sys.stdout.flush()
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
	        sys.stdout.write(res)
	        sys.stdout.flush()
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

