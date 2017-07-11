import os
import sys
import time
import socket
import datetime
import threading

from Utils import *
from dbManager import DbManager
from Output import Output
from Accounts import Accounts
import Sender


class SBProg:

	timers = {}
	timersTime = {}
	startSessionTime = ""

	MAX_NUM_ERRORS = 5

	def __init__(self, isTest = False):
		self.isTest = isTest
		self.output = Output("sbprog.log")
		self.write = self.output.write
		self.writeError = self.output.writeError


	def post_request(self, params):
		return Sender.post_request(self, params)


	def post_insta_request(self, params, firstTime=False):
		return Sender.post_insta_request(self, params)


	def runProgram(self):
		# try:
		self.printHello()
		if not self.tryConnectToRemoteServer():
			print "Closing.. bye."
		self.dbManager = DbManager()
		self.tryConnectDB()
		self.mainBOT()
		self.newEntry()
		# except Exception, e:
		# 	self.writeError("Error: Global Error.\n" + str(e))
		# 	print "Global Error"			
		# 	print e


	def printHello(self):
		print """$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\
$$$$$$$$$$$$$$$$$$$$$$$$$$   WELCOME SOCIAL BOT   $$$$$$$$$$$$$$$$$$$$$$$$$$\n\
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n"""


	def tryConnectToRemoteServer(self):
		"Look for the remote server"
		write("Trying connecting to server online.. ")
		resp = self.post_request({"action": "server_alive"})
		if resp != None:
			print "ok"
		else:
			return False
		write("Trying connecting to insta server online.. ")
		resp = self.post_insta_request({"action": "server_alive"})
		if resp != None:
			print "ok"
			return True
		else:
			return False


	def tryConnectDB(self):
		"Look for database"
		write("Look for database (" + self.dbManager.dbName + ").. ")
		if (not os.path.exists(self.dbManager.dbName)):
			print "not in path"
			self.dbManager.initDB()
		else:
			print "already in path!"
			self.dbManager.initDB()


	def mainBOT(self):
		print "Initializing the BOT:"
		self.startSessionTime = datetime.datetime.fromtimestamp(float(int(time.time()))).strftime('%H:%M:%S %d/%m')
		print "Get data from online server:"
		self.accounts = Accounts(self)
		print "Get data from online server complete!"
		self.updateStatistics(firstTime=True)
		if self.isTest:
			self.testConnectedBlogs()
		print "Initialization finished! Run the blogs!"


	def newEntry(self):
		while True:
			entry = raw_input("\n -> ")
			if entry in ["quit","exit"]:
				self.closing_operations()
				break
			elif entry in ["help","info"]:
				self.printHelpCmd()
			elif (entry != "") and (entry.split()[0] in ["clear","Clear"]):
				self.accounts.clearDB4blog(entry)
			elif (entry != "") and (entry.split()[0] in ["run","Run"]):
				self.accounts.runBlogs(entry)
				print "Running Blogs!"
			elif (entry != "") and (entry.split()[0] in ["stop","Stop"]):
				self.accounts.stopBlogs(entry)
			elif (entry != "") and (entry.split()[0] == "copy"):
				self.copyBlog(entry)
			else:
				print "Unknown command '" + entry + "'"


	def printHelpCmd(self):
		"Print list of available commands"
		print "List of commands:"
		print "   - 'help': for list of instructions"
		print "   - 'clean': clean directory"
		print "   - 'f': fast print"
		print "   - 'copy blog_to_copy my_blog': for copy an entire blog"
		print "   - 'run': for run a/all blog(s)"
		print "   - 'stop': for stop a/all blog(s)"
		print "   - 'quit': for quit"


	def closing_operations(self):
		print "Terminating program."
		self.accounts.closingOperations()
		try:
			self.timers["update"].cancel()
		except KeyError, msg:
			pass
		self.updateStatistics()
		resp = self.post_request({"action": "closing_operations", "stop_session_time": datetime.datetime.fromtimestamp(float(int(time.time()))).strftime('%H:%M:%S %d/%m')})
		print "   Bye!\n"


	def updateStatistics(self, firstTime=False):
		try:
			if firstTime:
				write("Update stats.. ")
			else:
				self.write("\tUpdate stats.. ")
			post_data_stats = {"action": "update_statistics",
				"Session_Start": self.startSessionTime,
				"Num_Threads": threading.activeCount(),
				"Num_Post_Like": self.dbManager.countAllPost(),
				"Num_Follow": self.dbManager.countAllFollow()}
			if "update" in self.timersTime:
				post_data_stats["Deadline_Update"] = self.timersTime["update"]
			up_stat = self.post_request(post_data_stats)
			if up_stat == None:
				if firstTime:
					print "Error: Update stats NOT ok (None up_stat)"
				else:
					self.writeError("Error: Update stats NOT ok (None up_stat)")
			else:
				if firstTime:
					print "ok!"
				else:
					self.write("\tok!")
		except KeyError, msg:
			if firstTime:
				print "KeyError on Update stats:\n" + str(msg)
			else:
				self.writeError("Error: KeyError on Update stats:\n" + str(msg))


	def copyBlog(self, entry):
		try:
			blog_to_copy = entry.split()[1]
			my_blog = self.accounts[self.matches[entry.split()[2]]]
			limit = int(entry.split()[3])
			counter = int(entry.split()[4])
			print "Creating new thread for copy the blog.. "
			t = threading.Thread(target=my_blog.copyBlog, args=(blog_to_copy,limit,counter)).start()
			self.updateStatistics()
		except IndexError, msg:
			print "   Syntax error: 'copy source myblog limit counter'"


	def testConnectedBlogs(self):
		print "\nBegin testing code:"
		account = self.accounts.accounts['1']
		account.initFollowers()
		account.initFollowings()
		account.unfollow()
		print "\nEnd testing code."
