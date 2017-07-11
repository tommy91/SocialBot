import sys

from Utils import *
from Account import *
from TumblrAccount import *
from InstagramAccount import *


class Accounts:

	TYPE_TUMBLR = 1
	TYPE_INSTAGRAM = 2

	ADD_OPERATION = '0'
	DELETE_OPERATION = '1'
	UPDATE_OPERATION = '2'

	def __init__(self, sbprog):
		self.app_accounts = {}
		self.accounts = {}
		self.matches = {}
		self.sbprog = sbprog
		self.isTest = sbprog.isTest
		self.timersTime = sbprog.timersTime
		self.timers = sbprog.timers
		self.write = sbprog.output.write
		self.writeError = sbprog.output.writeError
		self.updateStatistics = sbprog.updateStatistics
		self.post_request = sbprog.post_request
		self.initAccounts()
		self.updateBlogs(firstTime=True)


	def initAccounts(self):
		write("Get App Accounts.. ")
		appAccounts = self.post_request({"action": "get_app_accounts"})
		if appAccounts == None:
			print "\tError: None response."
			return
		print "ok"
		print "App Accounts:"
		counter = 0
		if len(appAccounts) == 0:
			print "\tNo app accounts fonud."
		else:
			for appAccount in appAccounts:
				print "\t" + str(counter + 1) + ") " + appAccount["Mail"] + " (id: " + appAccount["ID"] + ")"
				counter = counter + 1
				self.addAppAccount(appAccount)
		write("Get My Accounts.. ")
		myAccounts = self.post_request({"action": "get_my_accounts"})
		if myAccounts == None:
			print "\tError: None response."
			return
		print "ok"
		print "My Accounts:"
		counter = 0
		if len(myAccounts) == 0:
			print "\tNo accounts fonud."
		for myAccount in myAccounts:
			print "\t" + str(counter + 1) + ") " + myAccount["Mail"]
			counter = counter + 1
		if len(myAccounts) != 0:
			print "Get Accounts Data:"
			counter = 0
			for myAccount in myAccounts:
				write("\t" + str(counter + 1) + ") " + myAccount["Mail"] + " -> ")
				tags = self.post_request({"action": "get_tags", "ID": myAccount['ID']})
				otherAccounts = self.post_request({"action": "get_blogs", "ID": myAccount['ID']})
				if (tags == None) or (otherAccounts == None):
					continue
				self.addAccount(myAccount,tags,otherAccounts,firstTime=True)
				counter = counter + 1
				print "Done!"


	def addAppAccount(self, account):
		self.app_accounts[str(account['ID'])] = TumblrAppAccount(self, account)


	def addAccount(self, account, tags, blogs, firstTime=False):
		if int(account['Type']) == self.TYPE_TUMBLR:
			new_account = TumblrAccount(self, account, tags, blogs) 
		elif int(account['Type']) == self.TYPE_INSTAGRAM:
			new_account = InstagramAccount(self, account, tags, blogs)
		else:
			if firstTime:
				print "Error at addAccount for account " + str(account['Mail']) + ": get type " + str(account['Type'] + ".")
			else:
				self.writeError("Error at addAccount for account " + str(account['Mail']) + ": get type " + str(account['Type'] + "."))
			return
		self.accounts[str(account['ID'])] = new_account
		account_name = new_account.getAccountName()
		if account_name != "not available":
			self.matches[account_name] = account['ID']


	def updateBlogsData(self, firstTime=False):
		if firstTime:
			print "Update Blogs to DB:"
		else: 
			self.write("\tUpdate Blogs to DB:")
		for key, blog in self.accounts.iteritems():
			blog.updateBlogData()


	def synchOperations(self, firstTime=False):
		if firstTime:
			write("Clean up synchronization register.. ")
		else:
			self.write("\tSynchronize with online register.. ")
		synch_req = self.post_request({'action': "synch_operations"})
		if synch_req == None:
			if firstTime:
				print "Error: None response"
			else:
				self.writeError("Error: None response")
		else:
			if firstTime:
				print "ok"
			else:
				if len(synch_req) > 0:
					self.alreadySynchTags = []
					self.alreadySynchBlogs = []
					for up_row in synch_req:
						self.updateData(up_row)
				else:
					self.write("\talready synch!")


	def updateData(self, row):
		if row['Operation'] == self.ADD_OPERATION:
			self.updateAddOp(row['Table'],row['Blog'])
		elif row['Operation'] == self.DELETE_OPERATION:
			self.updateDelOp(row['Table'],row['Blog'])
		elif row['Operation'] == self.UPDATE_OPERATION:
			self.updateUpOp(row['Table'],row['Blog'])
		else:
			self.writeError("\t\tError: operation " + str(row['Operation']) + "unknown!")


	def updateAddOp(self, table, id_blog):
		if table == "sb_app_accounts":
			newAppAccount = self.post_request({"action": "get_app_accounts_ID", "id": id_blog})
			if newAppAccount != []:
				self.addAppAccount(newAppAccount[0])
				self.write("\t\tCreated new " + self.app_accounts[str(id_blog)].getSocialName() + " app account: '" + self.app_accounts[str(id_blog)].getAccountName() + "'")
			else:
				self.writeError("\t\t   Error: received empty list when try to get app account!")
		elif table == "sb_my_accounts":
			newMyAccount = self.post_request({"action": "get_my_accounts_ID", "id": id_blog})
			if newAccount != []:
				newTags = self.post_request({"action": "get_tags", "ID": id_blog})
				newBlogs = self.post_request({"action": "get_blogs", "ID": id_blog})
				self.addAccount(newMyAccount[0], newTags, newBlogs)
				self.write("\t\tCreated new " + self.accounts[str(id_blog)].getSocialName() + " account: '" + self.accounts[str(id_blog)].getAccountName() + "'")
				if newMyAccount[0]['State'] == self.accounts[str(id_blog)].STATUS_RUN:
					self.accounts[str(id_blog)].runBlog()
			else:
				self.writeError("\t\t   Error: received empty list when try to get account!")
		elif (table == "sb_other_accounts") or (table == "sb_tags"):
			self.write("\t\tTrying to add tags or blogs, operation not permitted!!! WTF is happening???")
		else:
			self.writeError("\t\tError: '" + table + "' is no a valid table!")


	def updateDelOp(self, table, id_blog):
		if table == "sb_app_accounts":
			self.write("\t\tRemoving " + self.app_accounts[str(id_blog)].getSocialName() + " app account '" + self.app_accounts[str(id_blog)].getAccountName() + "':")
			self.write("\t\t    removing dependencies for the app account:")
			for key, blog in self.accounts:
				if blog.app_account == id_blog:
					if blog.status == blog.STATUS_RUN:
						blog.stopBlog()
					self.write("\t\t        cleaning '" + blog.getAccountName() + "'.. ")
					blog.app_account = None
					blog.client = None
					blog.clientInfo = None
					self.write("ok")
			del self.app_accounts[str(id_blog)]
			self.write("\t\tRemoved!")
		elif table == "sb_my_accounts":
			self.write("\t\tRemoving " + self.accounts[str(id_blog)].getSocialName() + " account '" + self.accounts[str(id_blog)].getAccountName() + "':")
			if self.accounts[str(id_blog)].status == self.accounts[str(id_blog)].STATUS_RUN:
				self.accounts[str(id_blog)].stopBlog()
				self.accounts[str(id_blog)].clearDB()
			del self.matches[self.accounts[str(id_blog)].getAccountName()]
			del self.accounts[str(id_blog)]
			self.write("\t\tRemoved!")
		elif (table == "sb_other_accounts") or (table == "sb_tags"):
			self.writeError("\t\tTrying to delete tags or blogs, operation not permitted!!! WTF is happening???")
		else:
			self.writeError("\t\tError: '" + table + "' is no a valid table!")


	def updateUpOp(self, table, id_blog):
		if table == "sb_app_accounts":
			newAppAccount = self.post_request({"action": "get_app_accounts_ID", "id": id_blog})
			if newAppAccount != []:
				self.addAppAccount(newAppAccount[0])
			else:
				self.writeError("\t\t   Error: received empty list when try to get app account!")
		elif table == "sb_my_accounts":
			self.write("\t\tUpdate account for '" + self.accounts[str(id_blog)].getAccountName() + "':")
			newAccount = self.post_request({"action": "get_my_accounts_ID", "id": id_blog})
			if newAccount != []:
				self.accounts[str(id_blog)].updateUpOp(newAccount[0])
			else:
				self.writeError("\t\t   Error: received empty list when try to get account!")
		elif table == "sb_other_accounts": 
			if not id_blog in self.alreadySynchBlogs:
				self.write("\t\tUpdate blogs for '" + self.accounts[str(id_blog)].getAccountName() + "':")
				newBlogs = self.post_request({"action": "get_blogs", "ID": id_blog})
				self.accounts[str(id_blog)].blogs = blogs2list(newBlogs)
				for blog in self.accounts[str(id_blog)].blogs:
					self.write("\t\t    " + blog)
				self.alreadySynchBlogs.append(id_blog)
		elif table == "sb_tags":
			if not id_blog in self.alreadySynchTags:
				self.write("\t\tUpdate tags for '" + self.accounts[str(id_blog)].getAccountName() + "':")
				newTags = self.post_request({"action": "get_tags", "ID": id_blog})
				self.accounts[str(id_blog)].tags = tags2list(newTags)
				for tag in self.accounts[str(id_blog)].tags:
					self.write("\t\t    " + tag)
				self.alreadySynchTags.append(id_blog)
		else:
			self.writeError("\t\tError: '" + table + "' is no a valid table!")


	def clearDB4blog(self, entry):
		splitted = entry.split()
		if splitted[1] in ['help','Help']:
			print "'clear BLOG(all) TABLE(all)'"
			print "Blogs:"
			for key, blog in self.accounts.iteritems():
				print "\t" + blog.getAccountName()
			print "Tables:"
			for table in self.sbprog.dbManager.getTablesNames():
				print "\t" + table
		elif len(splitted) < 3:
			print "Need 2 params: 'clear BLOG(all) TABLE(all)'"
		else:
			try:
				if splitted[1] in ["all","All"]:
					if splitted[2] in ["all","All"]:
						print "Clear all tables for all blogs:"
						for key, blog in self.accounts.iteritems():
							blogname = blog.getAccountName()
							if blogname != "not available":
								write("\t" + blogname + " -> ")
								self.sbprog.dbManager.clearDB(blogname)
								print "ok."
					else:
						table = splitted[2]
						if not table in self.sbprog.dbManager.getTablesNames():
							print "Error: table '" + table + "' not found!" 
						else:
							print "Clear table '" + table + "' for all blogs:"
							for key, blog in self.accounts.iteritems():
								blogname = blog.getAccountName()
								if blogname != "not available":
									write("\t" + blogname + " -> ")
									self.sbprog.dbManager.clearTable4blog(blogname,table)
									print "ok."
				else:
					try:
						blogname = self.accounts[self.matches[splitted[1]]].getAccountName()
					except KeyError, msg:
						print "'" + splitted[1] + "' is not an existing account!"
					else:
						if blogname == "not available":
							print "Error: blogname not available"
						else:
							table = splitted[2]
							if table in ["all","All"]:
								write("Clear all tables for blog '" + blogname + "' -> ")
								self.sbprog.dbManager.clearDB(blogname)
								print "ok."
							else:
								if not table in self.sbprog.dbManager.getTablesNames():
									print "Error: table '" + table + "' not found!" 
								else:
									write("Clear table '" + table + "' for blog '" + blogname + "' -> ")
									self.sbprog.dbManager.clearTable4blog(blogname,table)
									print "ok."
			except IndexError, msg:
				print "   Syntax error: 'clear BLOG(all) TABLE(all)'"


	def runBlogs(self, entry):
		try:
			if entry.split()[1] in ["all","All"]:
				for key, blog in self.accounts.iteritems():
					if blog.getAccountName() != "not available":
						print "Running '" + blog.getAccountName() + "'"
						blog.runBlog()
					else:
						print "Cannot run not available blog! (id: " + blog.strID + ")"
			else:
				try:
					print "Running '" + entry.split()[1] + "'"
					self.accounts[self.matches[entry.split()[1]]].runBlog()
				except KeyError, msg:
					print entry.split()[1] + " is not an existing account!"
		except IndexError, msg:
			print "   Syntax error: 'run all' or 'run _blogname_'"


	def stopBlogs(self, entry):
		try:
			if entry.split()[1] in ["all","All"]:
				for kb,blog in self.accounts.iteritems():
					if blog.getAccountName() != "not available":
						blog.stopBlog()
						print "Stopped '" + blog.getAccountName() + "'"
				self.timers["update"].cancel()
				self.timers = {}
			else: 
				try:
					self.accounts[self.matches[entry.split()[1]]].stopBlog()
					print "Stopped '" + entry.split()[1] + "'"
				except KeyError, msg:
					print entry.split()[1] + " is not an existing blogname!"
		except IndexError, msg:
			print "   Syntax error: 'stop all' or 'stop _blogname_'"


	def setUpdateTimer(self):
		fiveMin = 60*5
		tup = threading.Timer(fiveMin, self.updateBlogs)
		tup.start()
		self.timers["update"] = tup
		deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + fiveMin)).strftime('%H:%M:%S %d/%m')
		self.timersTime["update"] = deadline


	def updateBlogs(self, firstTime=False):
		if firstTime:
			print "Update blogs info..\n" + "Update social data:"
		else:
			self.write("Update blogs info..")
			self.write("Update social data:")
		for kb,blog in self.accounts.iteritems():
			self.write("\tUpdate " + blog.getAccountName())
			blog.updateBlog(firstTime)
		self.updateBlogsData(firstTime)
		self.synchOperations(firstTime)
		if not self.isTest:
			self.setUpdateTimer()
		self.updateStatistics(firstTime)


	def closingOperations(self):
		for key, blog in self.accounts.iteritems():
			if blog.status == blog.STATUS_RUN:
				blog.stopBlog()

