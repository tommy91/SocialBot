import os
import sys
import socket
import datetime
import threading

import Utils
import dbManager
import Output
import Accounts
import Settings


class SBProg:

	timers = {}
	timersTime = {}
	startSessionTime = ""

	PATH_TO_SERVER = Settings.PATH_TO_SERVER
	RECEIVER = Settings.RECEIVER 

	def __init__(self, isTest = False):
		print "Creating new SBProg object.."
		self.isTest = isTest
		self.output = Output.Output()
		self.dbManager = dbManager.DbManager(self.output)
		print "SBProg object created."


	def runProgram(self):
		try:
			self.printHello()
			if not self.tryRemoteDBConnection():
				print "Closing.. bye."
			else:
				self.tryLocalDBConnection()
				self.mainBOT()
				self.newEntry()
		except Exception, e:
			print "Global Error."
			print e


	def printHello(self):
		print """$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\
	$$$$$$$$$$$$$$$$$$$$$$$$$$   WELCOME SOCIAL BOT   $$$$$$$$$$$$$$$$$$$$$$$$$$\n\
	$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n"""


	def tryRemoteDBConnection(self):
		"Look for the remote server"
		self.output.write("Trying remote DB connection.. ")
		resp = Utils.post_request({"action": "server_alive"})
		if resp != None:
			print "ok"
			return True
		else:
			return False


	def tryLocalDBConnection(self):
		"Look for database"
		dbName = self.dbManager.getDBName()
		self.output.write("Look for local DB (" + dbName + ").. ")
		if (not os.path.exists(dbName)):
			print "not in path"
			self.dbManager.initDB()
		else:
			print "already in path!"


	def mainBOT(self):
		print "Initializing the BOT:"
		self.startSessionTime = datetime.datetime.fromtimestamp(float(int(time.time()))).strftime('%H:%M:%S %d/%m')
		print "Get data from online server.."
		self.accounts = Accounts.Accounts(self)
		print "Get data from online server complete!"
		self.updateStatistics(firstTime=True)
		if self.isTest:
			self.testConnectedBlogs()
		print "Initialization finished! Run the blogs!"


	def newEntry():
		while True:
			entry = raw_input("\n" + self.output.startSimble)
			if entry in ["quit","exit"]:
				self.closing_operations()
				break
			elif entry in ["log"]:
				self.logResults()
			elif entry in ["help","info"]:
				self.printHelpCmd()
			elif (entry != "") and (entry.split()[0] in ["changeSpeed","speed","cs"]):
				self.output.changeSpeed(entry)
			elif (entry != "") and (entry.split()[0] in ["run","Run"]):
				self.accounts.runBlogs(entry)
			elif (entry != "") and (entry.split()[0] in ["stop","Stop"]):
				self.accounts.stopBlogs(entry)
			elif (entry != "") and (entry.split()[0] == "copy"):
				self.copyBlog(entry)
			else:
				self.output.write("Unknown command '" + entry + "'\n",True)


	def logResults(self):
		self.output.canWrite = True
		self.output.write("Logging results..\n")
		while not raw_input() in ['q','Q']:
			pass
		self.output.canWrite = False


	def printHelpCmd(self):
		"Print list of available commands"
		prevoutput.CanWrite = self.output.canWrite
		self.output.canWrite = True
		self.output.write("List of commands:\n",True)
		self.output.write("   - 'help': for list of instructions\n",True)
		self.output.write("   - 'changeSpeed': for changing printing text speed\n",True)
		self.output.write("   - 'copy blog_to_copy my_blog': for copy an entire blog\n",True)
		self.output.write("   - 'dbm': for open database manager console\n",True)
		self.output.write("   - 'run': for run a/all blog(s)\n",True)
		self.output.write("   - 'stop': for stop a/all blog(s)\n",True)
		self.output.write("   - 'quit': for quit\n",True)
		prevoutput.CanWrite = self.output.canWrite


	def closing_operations(self):
		self.output.canWrite = True
		self.output.write("Terminating program.\n")
		self.accounts.closingOperations()
		try:
			self.timers["update"].cancel()
		except KeyError, msg:
			pass
		self.updateStatistics()
		resp = post_request({"action": "closing_operations", "stop_session_time": datetime.datetime.fromtimestamp(float(int(time.time()))).strftime('%H:%M:%S %d/%m')})
		self.output.write("   Bye!\n\n")


	def updateStatistics(self, firstTime=False):
		try:
			if firstTime:
				self.output.write("Update stats.. ")
			else:
				self.output.write("\tUpdate stats.. ")
			post_data_stats = {"action": "update_statistics",
				"Session_Start": self.startSessionTime,
				"Num_Threads": threading.activeCount(),
				"Num_Post_Like": dbManager.countAllPost(),
				"Num_Follow": dbManager.countAllFollow()}
			if "update" in self.timersTime:
				post_data_stats["Deadline_Update"] = self.timersTime["update"]
			up_stat = post_request(post_data_stats)
			if up_stat != None:
				self.output.write("ok\n")
		except KeyError, msg:
			print "KeyError:"
			print str(msg)


	def copyBlog(self, entry):
		prevoutput.CanWrite = self.output.canWrite
		self.output.canWrite = True
		try:
			blog_to_copy = entry.split()[1]
			my_blog = self.accounts[matches[entry.split()[2]]]
			limit = int(entry.split()[3])
			counter = int(entry.split()[4])
			self.output.write("Creating new thread for copy the blog.. ",True)
			t = threading.Thread(target=my_blog.copyBlog, args=(blog_to_copy,limit,counter)).start()
			self.updateStatistics()
			self.output.canWrite = prevoutput.CanWrite
		except IndexError, msg:
			self.output.write("   Syntax error: 'copy source myblog limit counter'\n",True)
			self.output.canWrite = prevoutput.CanWrite


	def testConnectedBlogs(self):
		pass

