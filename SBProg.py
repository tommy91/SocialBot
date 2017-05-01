import os
import sys
import socket
import datetime

import dbManager
#import Settings

# Per debugging locale
import local_settings as Settings

class SBProg:

	isTest = False
	timers = {}
	timersTime = {}
	startSessionTime = ""

	PATH_TO_SERVER = Settings.PATH_TO_SERVER
	RECEIVER = Settings.RECEIVER 

	def __init__(self):
		try:
			self.output = Output()
			self.write = self.output.write
			self.writeln = self.output.writeln
	        self.printHello()
	        if not self.tryConnectToRemoteServer():
	            print "Closing.. bye."
	        self.tryConnectDB()
	        mainBOT()
	        newEntry()
	    except Exception, e:
	        print "Global Error."
	        print e


	def printHello(self):
	    self.write("""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\
	$$$$$$$$$$$$$$$$$$$$$$$$$$   WELCOME SOCIAL BOT   $$$$$$$$$$$$$$$$$$$$$$$$$$\n\
	$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\n""")


	def tryConnectToRemoteServer(self):
	    "Look for the remote server"
	    self.write("Trying connecting to server online.. ")
	    resp = post_request({"action": "server_alive"})
	    if resp != None:
	        print "ok"
	        return True
	    else:
	        return False


	def tryConnectDB(self):
	    "Look for database"
	    self.write("Look for database (" + dbManager.dbName + ").. ")
	    if (not os.path.exists(dbManager.dbName)):
	        self.write("not in path\n")
	        dbManager.initDB()
	    else:
	        self.write("already in path!\n")


	def mainBOT(self):
	    self.write("Initializing the BOT:\n")
	    self.startSessionTime = datetime.datetime.fromtimestamp(float(int(time.time()))).strftime('%H:%M:%S %d/%m')
	    self.write("Get data from online server:\n")
	  	self.accounts = Accounts(self)
	    self.write("Get data from online server complete!\n")
	    updateStatistics(firstTime=True)
	    if isTest:
	        testConnectedBlogs()
	    write("Initialization finished! Run the blogs!\n")


	def newEntry():
	    global timers, canWrite
	    while True:
	        entry = raw_input("\n" + startSimble)
	        if entry in ["quit","exit"]:
	            canWrite = True
	            closing_operations()
	            break
	        elif entry in ["log"]:
	            canWrite = True
	            logResults()
	        elif entry in ["help","info"]:
	            prevCanWrite = canWrite
	            canWrite = True
	            printHelpCmd()
	            prevCanWrite = canWrite
	    #     elif entry in ["dbmanager","dbm","dbManager","DBM"]:
	    #         write_console(myConsole.console, "Opening DB Manager Console.. ")
	    #         dBMConsole()
	        elif (entry != "") and (entry.split()[0] in ["changeSpeed","speed","cs"]):
	            changeSpeed(entry)
	        elif (entry != "") and (entry.split()[0] in ["run","Run"]):
	            try:
	                if entry.split()[1] in ["all","All"]:
	                    for key, blog in blogs.iteritems():
	                        if blog['type'] == 1: 
	                            if blog['data']['blogname'] != "not available":
	                                runBlog(blog['ID'])
	                            else:
	                                write("Cannot run not available blog! (id: " + blog['strID'] + ")\n",True)
	                        else:
	                            if blog['data']['name'] != "not available":
	                                runBlog(blog['ID'])
	                            else:
	                                write("Cannot run not available blog! (id: " + blog['strID'] + ")\n",True)
	                else:
	                    try:
	                        runBlog(matches[entry.split()[1]])
	                    except KeyError, msg:
	                        write(entry.split()[1] + " is not an existing blogname!\n",True)
	                if canWrite:
	                    logResults()
	            except IndexError, msg:
	                write("   Syntax error: 'run all' or 'run _blogname_'\n",True)
	        elif (entry != "") and (entry.split()[0] in ["stop","Stop"]):
	            try:
	                if entry.split()[1] in ["all","All"]:
	                    for kb,blog in blogs.iteritems():
	                        if blog['type'] == 1: 
	                            if blog['data']['blogname'] != "not available":
	                                stopBlog(blog['ID'])
	                        else:
	                            if blog['data']['name'] != "not available":
	                                stopBlog(blog['ID'])
	                    timers["update"].cancel()
	                    timers = {}
	                else: 
	                    try:
	                        stopBlog(matches[entry.split()[1]])
	                    except KeyError, msg:
	                        write(entry.split()[1] + " is not an existing blogname!\n",True)
	            except IndexError, msg:
	                write("   Syntax error: 'stop all' or 'stop _blogname_'\n",True)
	        elif (entry != "") and (entry.split()[0] == "copy"):
	            prevCanWrite = canWrite
	            canWrite = True
	            try:
	                blog_to_copy = entry.split()[1]
	                my_blog = entry.split()[2]
	                limit = int(entry.split()[3])
	                counter = int(entry.split()[4])
	                write("Creating new thread for copy the blog.. ",True)
	                t = threading.Thread(target=copyBlog, args=(blog_to_copy,my_blog,limit,counter)).start()
	                updateStatistics()
	                canWrite = prevCanWrite
	            except IndexError, msg:
	                write("   Syntax error: 'copy source myblog limit counter'\n",True)
	                canWrite = prevCanWrite


	def logResults():
	    global canWrite
	    write("Logging results..\n")
	    while not raw_input() in ['q','Q']:
	        pass
	    canWrite = False


	def printHelpCmd():
	    "Print list of available commands"
	    write("List of commands:\n",True)
	    write("   - 'help': for list of instructions\n",True)
	    write("   - 'changeSpeed': for changing printing text speed\n",True)
	    write("   - 'copy blog_to_copy my_blog': for copy an entire blog\n",True)
	    write("   - 'dbm': for open database manager console\n",True)
	    write("   - 'run': for run a/all blog(s)\n",True)
	    write("   - 'stop': for stop a/all blog(s)\n",True)
	    write("   - 'quit': for quit\n",True)


	def closing_operations():
	    global timers, blogs
	    write("Terminating program.\n")
	    for key, blog in blogs.iteritems():
	        if blog['status'] == STATUS_RUN:
	            stopBlog(blog['ID'])
	    try:
	        timers["update"].cancel()
	    except KeyError, msg:
	        pass
	    updateStatistics()
	    resp = post_request({"action": "closing_operations", "stop_session_time": datetime.datetime.fromtimestamp(float(int(time.time()))).strftime('%H:%M:%S %d/%m')})
	    write("   Bye!\n\n")

