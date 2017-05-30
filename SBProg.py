import os
import sys
import time
import socket
import datetime
import threading

import requests
from httplib2 import ServerNotFoundError
from requests.exceptions import ConnectionError, Timeout, HTTPError

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
			print "Closing.. bye."
		self.dbManager = DbManager(self.output)
		self.tryConnectDB()
		self.mainBOT()
		self.newEntry()
		# except Exception, e:
		# 	self.write("Global Error.\n")
		# 	self.write(str(e) + "\n")


	def printHello(self):
		print """$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\
$$$$$$$$$$$$$$$$$$$$$$$$$$   WELCOME SOCIAL BOT   $$$$$$$$$$$$$$$$$$$$$$$$$$\n\
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n"""


	def tryConnectToRemoteServer(self):
		"Look for the remote server"
		sys.stdout.write("Trying connecting to server online.. ")
		resp = self.post_request({"action": "server_alive"})
		if resp != None:
			print "ok"
			return True
		else:
			return False


	def tryConnectDB(self):
		"Look for database"
		sys.stdout.write("Look for database (" + self.dbManager.dbName + ").. ")
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
			entry = raw_input("\n" + self.output.startSimble)
			if entry in ["quit","exit"]:
				self.closing_operations()
				break
			elif entry in ["help","info"]:
				self.printHelpCmd()
			elif (entry != "") and (entry.split()[0] in ["clear","Clear"]):
				self.accounts.clearDB4blog(entry)
			elif (entry != "") and (entry.split()[0] in ["log","Log"]):
				self.accounts.log(entry)
			elif (entry != "") and (entry.split()[0] in ["changeSpeed","speed","cs"]):
				self.output.changeSpeed(entry)
			elif (entry != "") and (entry.split()[0] in ["run","Run"]):
				# self.accounts.runBlogs(entry)
				print "Running Blogs!"
				t = threading.Thread(target=self.accounts.runBlogs, args=(entry,)).start()
			elif (entry != "") and (entry.split()[0] in ["stop","Stop"]):
				self.accounts.stopBlogs(entry)
			elif (entry != "") and (entry.split()[0] == "copy"):
				self.copyBlog(entry)
			else:
				print "Unknown command '" + entry + "'"


	def logResults(self):
		self.canWrite = True
		print "\nLogging results.."
		while not raw_input() in ['q','Q']:
			pass
		self.canWrite = False


	def printHelpCmd(self):
		"Print list of available commands"
		prevCanWrite = self.canWrite
		self.canWrite = True
		print "List of commands:"
		print "   - 'help': for list of instructions"
		print "   - 'clean': clean directory"
		print "   - 'f': fast print"
		print "   - 'changeSpeed': for changing printing text speed"
		print "   - 'copy blog_to_copy my_blog': for copy an entire blog"
		print "   - 'run': for run a/all blog(s)"
		print "   - 'stop': for stop a/all blog(s)"
		print "   - 'quit': for quit"
		prevCanWrite = self.canWrite


	def closing_operations(self):
		self.canWrite = True
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
				sys.stdout.write("Update stats.. ")
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
					self.write("Error: Update stats NOT ok (None up_stat)\n")
			else:
				if firstTime:
					print "ok!"
				else:
					self.write("ok!\n")
		except KeyError, msg:
			if firstTime:
				print "KeyError on Update stats:\n" + str(msg)
			else:
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
			print "Creating new thread for copy the blog.. "
			t = threading.Thread(target=my_blog.copyBlog, args=(blog_to_copy,limit,counter)).start()
			self.updateStatistics()
			self.canWrite = prevCanWrite
		except IndexError, msg:
			print "   Syntax error: 'copy source myblog limit counter'"
			self.canWrite = prevCanWrite


	def testConnectedBlogs(self):
		print "\nBegin testing code:"
		account = self.accounts.accounts['1']
		account.initFollowers()
		account.initFollowings()
		account.unfollow()
		print "\nEnd testing code."


	def post_request(self, post_data):
		try:
			return self.send_and_check_request(post_data)
		except HTTPError as e:
			self.write(str(e) + "\n")
			return None


	def send_and_check_request(self, post_data):
		try:
			resp = requests.post(Settings.PATH_TO_SERVER + Settings.RECEIVER, data = post_data)
			if resp.status_code == 200:
				try:
					parsed = resp.json()
					if 'Error' in parsed:
						self.write("Error: " + str(parsed['Error']) + "\n")
						return None
					else:
						return parsed['Result']
				except ValueError as e:
					self.write("ValueError:\n")
					self.write(str(resp.content) + "\n")
					return None
			else:
				resp.raise_for_status()
		except ConnectionError as e:
			self.write("ConnectionError:\n")
			self.write(str(e) + "\n")
			return None 
		except Timeout as e:
			self.write("Timeout Error:\n")
			self.write(str(e) + "\n")
			return None
