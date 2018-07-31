import os
import sys
import time
import socket
import datetime
import threading

import Utils
import dbManager
import Output
import Accounts
import Sender


class SBProg:

	timers = {}
	timersTime = {}
	startSessionTime = ""

	MAX_NUM_ERRORS = 5

	def __init__(self, isTest = False):
		self.isTest = isTest
		self.output = Output.Output("sbprog")
		self.dbManager = dbManager.DbManager()


	def post_request(self, params):
		return Sender.post_request(self, params)


	def post_insta_request(self, params, firstTime=False):
		return Sender.post_insta_request(self, params)


	def runProgram(self):
		# try:
		self.printHello()
		if not self.tryRemoteDBConnection():
			print "Closing.. bye."
		else:
			self.dbManager.tryDBConnection()
			self.mainBOT()
			self.newEntry()
		# except Exception, e:
		# 	self.output.writeError("Error: Global Error.\n" + str(e))
		# 	print "Global Error"			
		# 	print e


	def printHello(self):
		print """$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\
$$$$$$$$$$$$$$$$$$$$$$$$$$   WELCOME SOCIAL BOT   $$$$$$$$$$$$$$$$$$$$$$$$$$\n\
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n"""


	def tryRemoteDBConnection(self):
		"Look for the remote server"
		self.output.write("Trying connecting to remote server and DB.. ")
		resp = self.post_request({"action": "server_alive"})
		if resp != None:
			print "ok"
		else:
			return False
		self.output.write("Trying connecting to insta server online.. ")
		resp = self.post_insta_request({"action": "server_alive"})
		if resp != None:
			print "ok"
			return True
		else:
			return False


	def mainBOT(self):
		print "Initializing the BOT:"
		self.startSessionTime = datetime.datetime.fromtimestamp(float(int(time.time()))).strftime('%H:%M:%S %d/%m')
		print "Get data from online server:"
		self.accounts = Accounts.Accounts(self)
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
			elif (entry != "") and (entry.split()[0] in ["clear"]):
				self.accounts.clearDB4blog(entry)
			elif (entry != "") and (entry.split()[0] in ["run"]):
				self.accounts.runBlogs(entry)
				print "Running Blogs!"
			elif (entry != "") and (entry.split()[0] in ["stop"]):
				self.accounts.stopBlogs(entry)
			else:
				print "Unknown command '" + entry + "'"


	def printHelpCmd(self):
		"Print list of available commands"
		print "List of commands:"
		print "   - 'help': for list of instructions"
		print "   - 'clear': clean directory"
		print "   - 'run': for run a/all blog(s)"
		print "   - 'stop': for stop a/all blog(s)"
		print "   - 'quit/exit': for quit"


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
				self.output.write("Update stats.. ")
			else:
				self.output.writeLog("\tUpdate stats.. ")
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
					self.output.writeErrorLog("Error: Update stats NOT ok (None up_stat)\n")
			else:
				if firstTime:
					print "ok!"
				else:
					self.output.writeLog("\tok!\n")
		except KeyError, msg:
			if firstTime:
				print "KeyError on Update stats:\n" + str(msg)
			else:
				self.output.writeErrorLog("Error: KeyError on Update stats:\n" + str(msg) + "\n")


	def testConnectedBlogs(self):
		print "\nBegin testing code:"
		account = self.accounts.accounts['1']
		account.initFollowers()
		account.initFollowings()
		account.unfollow()
		print "\nEnd testing code."
