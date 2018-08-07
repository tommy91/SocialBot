import sys
import threading

import Utils
import Account
import InstagramAccount


class Accounts:

	TYPE_TUMBLR = 1
	TYPE_INSTAGRAM = 2

	ADD_OPERATION = '0'
	DELETE_OPERATION = '1'
	UPDATE_OPERATION = '2'

	def __init__(self, sbprog):
		self.instagramAccounts = {}
		self.matches = {}
		self.sbprog = sbprog
		self.output = sbprog.output
		self.post_request = sbprog.post_request
		self.initAccounts()
		self.updateAccounts(firstTime=True)


	def initAccounts(self):
		self.initInstagramAccounts()


	def initInstagramAccounts(self):
		self.output.write("Get Instagram Accounts.. ")
		instagramAccounts = self.post_request({"action": "get_instagram_accounts"})
		if instagramAccounts == None:
			print "\tError: None response."
			return
		print "ok"
		print "Instagram Accounts:"
		if len(instagramAccounts) == 0:
			print "\tNo accounts found."
		else:
			counter = 1
			for instaAccount in instagramAccounts:
				print "\t" + str(counter) + ") " + instaAccount["Mail"]
				counter += 1
			print "Get Instagram Accounts Data:"
			counter = 1
			for instaAccount in instagramAccounts:
				self.output.write("\t" + str(counter) + ") " + instaAccount["Mail"] + " -> tags.. ")
				tags = self.post_request({"action": "get_tags", "ID": instaAccount['ID']})
				blogs = self.post_request({"action": "get_blogs", "ID": instaAccount['ID']})
				if (tags == None) or (blogs == None):
					# error in response
					continue
				self.addInstagramAccount(instaAccount,tags,blogs)
				counter += 1
				print "Done!"


	def addAccount(self, account, tags, blogs):
		if account['Type'] == TYPE_TUMBLR:
			pass # ToDo
		elif account['Type'] == TYPE_INSTAGRAM:
			self.addInstagramAccount(account, tags, blogs)
		else:
			self.output.writeErrorLog("Error: account type '" + account['Type'] + "' for " + account['Name'] + " unknown!\n")



	def addInstagramAccount(self, account, tags, blogs):
		new_insta_account = InstagramAccount.InstagramAccount(self, account, tags, blogs)
		self.instagramAccounts[str(account['ID'])] = new_insta_account
		self.matches[account['Name']] = account['ID']


	def updateAccountsData(self, firstTime=False):
		if firstTime:
			print "Update Accounts to DB:"
		else: 
			self.output.writeLog("\tUpdate Blogs to DB:\n")
		for key, blog in self.instagramAccounts.iteritems():
			blog.updateAccountData(firstTime)


	def synchOperations(self, firstTime=False):
		if firstTime:
			self.output.write("Clean up synchronization register.. ")
		else:
			self.output.writeLog("\tSynchronize with online register.. ")
		synch_req = self.post_request({'action': "synch_operations"})
		if synch_req == None:
			if firstTime:
				print "Error: None response"
			else:
				self.output.writeErrorLog("Error: None response\n")
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
					self.output.writeLog("\talready synch!\n")


	def updateData(self, row):
		if row['Operation'] == self.ADD_OPERATION:
			self.updateAddOp(row['Table'],row['Blog'])
		elif row['Operation'] == self.DELETE_OPERATION:
			self.updateDelOp(row['Table'],row['Blog'])
		elif row['Operation'] == self.UPDATE_OPERATION:
			self.updateUpOp(row['Table'],row['Blog'])
		else:
			self.output.writeErrorLog("\t\tError: operation " + str(row['Operation']) + "unknown!\n")


	def updateAddOp(self, table, id_blog):
		if table == "sb_my_accounts":
			newMyAccount = self.post_request({"action": "get_account_by_id", "id": id_blog})
			if newAccount != []:
				newTags = self.post_request({"action": "get_tags", "ID": id_blog})
				newBlogs = self.post_request({"action": "get_blogs", "ID": id_blog})
				self.addAccount(newMyAccount[0], newTags, newBlogs)
				self.output.writeLog("\t\tCreated new " + self.accounts[str(id_blog)].getSocialName() + " account: '" + self.accounts[str(id_blog)].getAccountName() + "'\n")
				if newMyAccount[0]['State'] == self.accounts[str(id_blog)].STATUS_RUN:
					self.accounts[str(id_blog)].runBlog()
			else:
				self.output.writeErrorLog("\t\t   Error: received empty list when try to get account!\n")
		elif (table == "sb_other_accounts") or (table == "sb_tags"):
			self.output.writeErrorLog("\t\tError: Trying to add tags or blogs, operation not permitted!!! WTF is happening???\n")
		else:
			self.output.writeErrorLog("\t\tError: '" + table + "' is no a valid table!\n")


	def updateDelOp(self, table, id_blog):
		if table == "sb_my_accounts":
			self.output.writeLog("\t\tRemoving " + self.accounts[str(id_blog)].getSocialName() + " account '" + self.accounts[str(id_blog)].getAccountName() + "':\n")
			if self.accounts[str(id_blog)].status == self.accounts[str(id_blog)].STATUS_RUN:
				self.accounts[str(id_blog)].stopBlog()
				self.accounts[str(id_blog)].clearDB()
			del self.matches[self.accounts[str(id_blog)].getAccountName()]
			del self.accounts[str(id_blog)]
			self.output.writeLog("\t\tRemoved!\n")
		elif (table == "sb_other_accounts") or (table == "sb_tags"):
			self.output.writeErrorLog("\t\tError: Trying to delete tags or blogs, operation not permitted!!! WTF is happening???\n")
		else:
			self.output.writeErrorLog("\t\tError: '" + table + "' is no a valid table!\n")


	def updateUpOp(self, table, id_blog):
		if table == "sb_my_accounts":
			self.output.writeLog("\t\tUpdate account for '" + self.accounts[str(id_blog)].getAccountName() + "':\n")
			newAccount = self.post_request({"action": "get_account_by_id", "id": id_blog})
			if newAccount != []:
				self.accounts[str(id_blog)].updateUpOp(newAccount[0])
			else:
				self.output.writeErrorLog("\t\t   Error: received empty list when try to get account!\n")
		elif table == "sb_other_accounts": 
			if not id_blog in self.alreadySynchBlogs:
				self.output.writeLog("\t\tUpdate blogs for '" + self.accounts[str(id_blog)].getAccountName() + "':\n")
				newBlogs = self.post_request({"action": "get_blogs", "ID": id_blog})
				self.accounts[str(id_blog)].blogs = Utils.blogs2list(newBlogs)
				for blog in self.accounts[str(id_blog)].blogs:
					self.output.writeLog("\t\t    " + blog + "\n")
				self.alreadySynchBlogs.append(id_blog)
		elif table == "sb_tags":
			if not id_blog in self.alreadySynchTags:
				self.output.writeLog("\t\tUpdate tags for '" + self.accounts[str(id_blog)].getAccountName() + "':\n")
				newTags = self.post_request({"action": "get_tags", "ID": id_blog})
				self.accounts[str(id_blog)].tags = Utils.tags2list(newTags)
				for tag in self.accounts[str(id_blog)].tags:
					self.output.writeLog("\t\t    " + tag + "\n")
				self.alreadySynchTags.append(id_blog)
		else:
			self.output.writeErrorLog("\t\tError: '" + table + "' is no a valid table!\n")


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
								self.output.write("\t" + blogname + " -> ")
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
									self.output.write("\t" + blogname + " -> ")
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
								self.output.write("Clear all tables for blog '" + blogname + "' -> ")
								self.sbprog.dbManager.clearDB(blogname)
								print "ok."
							else:
								if not table in self.sbprog.dbManager.getTablesNames():
									print "Error: table '" + table + "' not found!" 
								else:
									self.output.write("Clear table '" + table + "' for blog '" + blogname + "' -> ")
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
		tup = threading.Timer(fiveMin, self.updateAccounts)
		tup.start()
		self.timers["update"] = tup
		deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + fiveMin)).strftime('%H:%M:%S %d/%m')
		self.timersTime["update"] = deadline


	def updateAccounts(self, firstTime=False):
		if firstTime:
			print "Update blogs info..\n" + "Update social data:"
		else:
			self.output.writeLog("Update blogs info..\n")
			self.output.writeLog("Update social data:\n")
		# update instagrama accounts
		for kb,blog in self.instagramAccounts.iteritems():
			self.output.writeLog("\tUpdate " + blog.getAccountName() + "\n")
			blog.updateAccount(firstTime)
		self.updateAccountsData(firstTime)
		self.synchOperations(firstTime)
		if not self.sbprog.isTest:
			self.setUpdateTimer()
		self.updateStatistics(firstTime)


	def closingOperations(self):
		for key, blog in self.accounts.iteritems():
			if blog.status == blog.STATUS_RUN:
				blog.stopBlog()

