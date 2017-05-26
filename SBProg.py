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
import Settings


class SBProg:

	timers = {}
	timersTime = {}
	startSessionTime = ""

	PATH_TO_SERVER = Settings.PATH_TO_SERVER
	RECEIVER = Settings.RECEIVER 

	def __init__(self, sleepChar=None, sleepLine=None, isTest = False):
		self.isTest = isTest
		self.sleepChar = sleepChar
		self.sleepLine = sleepLine


	def runProgram(self):
		# try:
		self.output = Output(sleepChar=self.sleepChar, sleepLine=self.sleepLine)
		self.write = self.output.write
		self.writeln = self.output.writeln
		self.canWrite = self.output.canWrite
		self.printHello()
		if not self.tryConnectToRemoteServer():
			self.write("Closing.. bye.\n")
		self.dbManager = DbManager(self.output)
		self.tryConnectDB()
		self.mainBOT()
		self.newEntry()
		# except Exception, e:
		# 	self.write("Global Error.\n")
		# 	self.write(str(e) + "\n")


	def printHello(self):
		self.write("""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\
$$$$$$$$$$$$$$$$$$$$$$$$$$   WELCOME SOCIAL BOT   $$$$$$$$$$$$$$$$$$$$$$$$$$\n\
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\n""")


	def tryConnectToRemoteServer(self):
		"Look for the remote server"
		self.write("Trying connecting to server online.. ")
		resp = post_request({"action": "server_alive"})
		if resp != None:
			self.write("ok\n")
			return True
		else:
			return False


	def tryConnectDB(self):
		"Look for database"
		self.write("Look for database (" + self.dbManager.dbName + ").. ")
		if (not os.path.exists(self.dbManager.dbName)):
			self.write("not in path\n")
			self.dbManager.initDB()
		else:
			self.write("already in path!\n")
			self.dbManager.initDB()


	def mainBOT(self):
		self.write("Initializing the BOT:\n")
		self.startSessionTime = datetime.datetime.fromtimestamp(float(int(time.time()))).strftime('%H:%M:%S %d/%m')
		self.write("Get data from online server:\n")
		self.accounts = Accounts(self)
		self.write("Get data from online server complete!\n")
		self.updateStatistics(firstTime=True)
		if self.isTest:
			self.testConnectedBlogs()
		self.write("Initialization finished! Run the blogs!\n")


	def newEntry(self):
		while True:
			entry = raw_input("\n" + self.output.startSimble)
			if entry in ["quit","exit"]:
				self.closing_operations()
				break
			elif entry in ["help","info"]:
				self.printHelpCmd()
			elif (entry != "") and (entry.split()[0] in ["log","Log"]):
				self.accounts.log(entry)
			elif (entry != "") and (entry.split()[0] in ["changeSpeed","speed","cs"]):
				self.output.changeSpeed(entry)
			elif (entry != "") and (entry.split()[0] in ["run","Run"]):
				self.accounts.runBlogs(entry)
			elif (entry != "") and (entry.split()[0] in ["stop","Stop"]):
				self.accounts.stopBlogs(entry)
			elif (entry != "") and (entry.split()[0] == "copy"):
				self.copyBlog(entry)
			else:
				self.write("Unknown command '" + entry + "'\n",True)


	def logResults(self):
		self.canWrite = True
		self.write("\nLogging results..\n")
		while not raw_input() in ['q','Q']:
			pass
		self.canWrite = False


	def printHelpCmd(self):
		"Print list of available commands"
		prevCanWrite = self.canWrite
		self.canWrite = True
		self.write("List of commands:\n",True)
		self.write("   - 'help': for list of instructions\n",True)
		self.write("   - 'clean': clean directory\n",True)
		self.write("   - 'f': fast print\n",True)
		self.write("   - 'changeSpeed': for changing printing text speed\n",True)
		self.write("   - 'copy blog_to_copy my_blog': for copy an entire blog\n",True)
		self.write("   - 'run': for run a/all blog(s)\n",True)
		self.write("   - 'stop': for stop a/all blog(s)\n",True)
		self.write("   - 'quit': for quit\n",True)
		prevCanWrite = self.canWrite


	def closing_operations(self):
		self.canWrite = True
		self.write("Terminating program.\n")
		self.accounts.closingOperations()
		try:
			self.timers["update"].cancel()
		except KeyError, msg:
			pass
		self.updateStatistics()
		resp = post_request({"action": "closing_operations", "stop_session_time": datetime.datetime.fromtimestamp(float(int(time.time()))).strftime('%H:%M:%S %d/%m')})
		self.write("   Bye!\n\n")


	def updateStatistics(self, firstTime=False):
		try:
			if firstTime:
				self.write("Update stats.. ")
			# else:
			# 	self.write("\tUpdate stats.. ")
			post_data_stats = {"action": "update_statistics",
				"Session_Start": self.startSessionTime,
				"Num_Threads": threading.activeCount(),
				"Num_Post_Like": self.dbManager.countAllPost(),
				"Num_Follow": self.dbManager.countAllFollow()}
			if "update" in self.timersTime:
				post_data_stats["Deadline_Update"] = self.timersTime["update"]
			up_stat = post_request(post_data_stats)
			if up_stat == None:
				self.write("Error: Update stats NOT ok (None up_stat)\n")
			else:
				if firstTime:
					self.write("ok!\n")
		except KeyError, msg:
			self.write("KeyError on Update stats:\n")
			self.write(str(msg) + "\n")


	def copyBlog(self, entry):
		prevCanWrite = self.canWrite
		self.canWrite = True
		try:
			blog_to_copy = entry.split()[1]
			my_blog = self.accounts[self.matches[entry.split()[2]]]
			limit = int(entry.split()[3])
			counter = int(entry.split()[4])
			self.write("Creating new thread for copy the blog.. ",True)
			t = threading.Thread(target=my_blog.copyBlog, args=(blog_to_copy,limit,counter)).start()
			self.updateStatistics()
			self.canWrite = prevCanWrite
		except IndexError, msg:
			self.write("   Syntax error: 'copy source myblog limit counter'\n",True)
			self.canWrite = prevCanWrite


	def testConnectedBlogs(self):
		self.write("\nBegin testing code:\n")
		for key, account in self.accounts.accounts.iteritems():
			# run
			account.lock.acquire()
			prevCanWrite = account.canWrite
			account.canWrite = True
			account.checkData()
			account.updateBlog()
			account.initFollowers()
			account.initFollowings()
			account.write("\t" + account.getAccountName() + " is running.\n")
			account.status = account.STATUS_RUN
			account.updateBlogData()
			account.updateStatistics()
			account.canWrite = prevCanWrite
			account.lock.release()
			# execute
			if account.account_type == 1:
				account.post(num_posts=1)
			account.follow(num_follows=1, isDump=True)
			account.like(num_likes=1, isDump=True)
			# stop
			account.lock.acquire()
			prevCanWrite = account.canWrite
			account.canWrite = True
			account.writeln("Stop " + account.getAccountName() + ".. \n")
			account.status = account.STATUS_STOP
			account.updateBlogData()
			account.updateStatistics()
			account.write("\t" + account.getAccountName() + " stopped.\n")
			account.canWrite = prevCanWrite
			account.lock.release()
		self.write("\nEnd testing code.\n")
