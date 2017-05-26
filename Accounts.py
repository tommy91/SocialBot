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
		self.writeln = sbprog.output.writeln
		self.canWrite = sbprog.output.canWrite
		self.lock = sbprog.output.lock
		self.updateStatistics = sbprog.updateStatistics
		self.initAccounts()
		self.updateBlogs(firstTime=True)


	def initAccounts(self):
		self.write("Get App Accounts.. ")
		appAccounts = post_request({"action": "get_app_accounts"})
		if appAccounts == None:
			self.write("\tError: None response.\n")
			return
		self.write("ok\n")
		self.write("App Accounts:\n")
		counter = 0
		if len(appAccounts) == 0:
			self.write("\tNo app accounts fonud.\n")
		else:
			for appAccount in appAccounts:
				self.write("\t" + str(counter + 1) + ") " + appAccount["Mail"] + " (id: " + appAccount["ID"] + ")" + "\n")
				counter = counter + 1
				self.addAppAccount(appAccount)
		self.write("Get My Accounts.. ")
		myAccounts = post_request({"action": "get_my_accounts"})
		if myAccounts == None:
			self.write("\tError: None response.\n")
			return
		self.write("ok\n")
		self.write("My Accounts:\n")
		counter = 0
		if len(myAccounts) == 0:
			self.write("\tNo accounts fonud.\n")
		for myAccount in myAccounts:
			self.write("\t" + str(counter + 1) + ") " + myAccount["Mail"] + "\n")
			counter = counter + 1
		if len(myAccounts) != 0:
			self.write("Get Accounts Data:\n")
			counter = 0
			for myAccount in myAccounts:
				self.write("\t" + str(counter + 1) + ") " + myAccount["Mail"] + " -> ")
				tags = post_request({"action": "get_tags", "ID": myAccount['ID']})
				otherAccounts = post_request({"action": "get_blogs", "ID": myAccount['ID']})
				if (tags == None) or (otherAccounts == None):
					continue
				self.addAccount(myAccount,tags,otherAccounts)
				counter = counter + 1
				self.write("Done!\n")


	def addAppAccount(self, account):
		self.app_accounts[str(account['ID'])] = TumblrAppAccount(self, account)


	def addAccount(self, account, tags, blogs):
		if int(account['Type']) == self.TYPE_TUMBLR:
			new_account = TumblrAccount(self, account, tags, blogs) 
		elif int(account['Type']) == self.TYPE_INSTAGRAM:
			new_account = InstagramAccount(self, account, tags, blogs)
		else:
			self.write("Error at addAccount for account " + str(account['Mail']) + ": get type " + str(account['Type'] + "."))
			return
		self.accounts[str(account['ID'])] = new_account
		account_name = new_account.getAccountName()
		if account_name != "not available":
			self.matches[account_name] = account['ID']


	def updateBlogsData(self, firstTime=False):
		if firstTime:
			self.write("Update Blogs to DB:\n")
		else: 
			self.write("\tUpdate Blogs to DB:\n")
		for key, blog in self.accounts.iteritems():
			blog.updateBlogData()


	def synchOperations(self, firstTime=False):
		if firstTime:
			self.write("Clean up synchronization register.. ")
		else:
			self.write("\tSynchronize with online register.. ")
		synch_req = post_request({'action': "synch_operations"})
		if firstTime:
			self.write("ok\n")
		else:
			if len(synch_req) > 0:
				self.write("\n")
				for up_row in synch_req:
					self.updateData(up_row)
			else:
				self.write("already synch!\n")


	def updateData(self, row):
		if row['Operation'] == self.ADD_OPERATION:
			self.updateAddOp(row['Table'],row['Blog'])
		elif row['Operation'] == self.DELETE_OPERATION:
			self.updateDelOp(row['Table'],row['Blog'])
		elif row['Operation'] == self.UPDATE_OPERATION:
			self.updateUpOp(row['Table'],row['Blog'])
		else:
			self.write("\t\tError: operation " + str(row['Operation']) + "unknown!\n")


	def updateAddOp(self, table, id_blog):
		if table == "sb_app_accounts":
			newAppAccount = post_request({"action": "get_app_accounts_ID", "id": id_blog})
			if newAppAccount != []:
				self.addAppAccount(newAppAccount[0])
				self.write("\t\tCreated new " + self.app_accounts[str(id_blog)].getSocialName() + " app account: '" + self.app_accounts[str(id_blog)].getAccountName() + "'\n")
			else:
				self.write("\t\t   Error: received empty list when try to get app account!\n")
		elif table == "sb_my_accounts":
			newMyAccount = post_request({"action": "get_my_accounts_ID", "id": id_blog})
			if newAccount != []:
				newTags = post_request({"action": "get_tags", "id": id_blog})
				newBlogs = post_request({"action": "get_blogs", "id": id_blog})
				self.addAccount(newMyAccount[0], newTags, newBlogs)
				self.write("\t\tCreated new " + self.accounts[str(id_blog)].getSocialName() + " account: '" + self.accounts[str(id_blog)].getAccountName() + "'\n")
				if newMyAccount[0]['status'] == self.accounts[str(id_blog)].STATUS_RUN:
					self.accounts[str(id_blog)].runBlog()
			else:
				self.write("\t\t   Error: received empty list when try to get account!\n")
		elif (table == "sb_other_accounts") or (table == "sb_tags"):
			self.write("\t\tTrying to add tags or blogs, operation not permitted!!! WTF is happening???\n")
		else:
			self.write("\t\tError: '" + table + "' is no a valid table!\n")


	def updateDelOp(self, table, id_blog):
		if table == "sb_app_accounts":
			self.write("\t\tRemoving " + self.app_accounts[str(id_blog)].getSocialName() + " app account '" + self.app_accounts[str(id_blog)].getAccountName() + "':\n")
			self.write("\t\t    removing dependencies for the app account:\n")
			for key, blog in self.accounts:
				if blog.app_account == id_blog:
					if blog.status == blog.STATUS_RUN:
						blog.stopBlog()
					self.write("\t\t        cleaning '" + blog.getAccountName() + "'.. ")
					blog.app_account = None
					blog.client = None
					blog.clientInfo = None
					self.write("ok\n")
			del self.app_accounts[str(id_blog)]
			self.write("\t\tRemoved!\n")
		elif table == "sb_my_accounts":
			self.write("\t\tRemoving " + self.accounts[str(id_blog)].getSocialName() + " account '" + self.accounts[str(id_blog)].getAccountName() + "':\n")
			if self.accounts[str(id_blog)].status == self.accounts[str(id_blog)].STATUS_RUN:
				self.accounts[str(id_blog)].stopBlog()
				self.accounts[str(id_blog)].clearDB()
			del self.matches[self.accounts[str(id_blog)].getAccountName()]
			del self.accounts[str(id_blog)]
			self.write("\t\tRemoved!\n")
		elif (table == "sb_other_accounts") or (table == "sb_tags"):
			self.write("\t\tTrying to delete tags or blogs, operation not permitted!!! WTF is happening???\n")
		else:
			self.write("\t\tError: '" + table + "' is no a valid table!\n")


	def updateUpOp(self, table, id_blog):
		if table == "sb_app_accounts":
			newAppAccount = post_request({"action": "get_app_accounts_ID", "id": id_blog})
			if newAppAccount != []:
				self.addAppAccount(newAppAccount[0])
			else:
				self.write("\t\t   Error: received empty list when try to get app account!\n")
		elif table == "sb_my_accounts":
			self.write("\t\tUpdate account for '" + self.accounts[str(id_blog)].getAccountName() + "':\n")
			newAccount = post_request({"action": "get_my_accounts_ID", "id": id_blog})
			if newAccount != []:
				self.accounts[str(id_blog)].updateUpOp(newAccount[0])
			else:
				self.write("\t\t   Error: received empty list when try to get account!\n")
		elif table == "sb_other_accounts":
			self.write("\t\tUpdate blogs for '" + self.accounts[str(id_blog)].getAccountName() + "':\n")
			newBlogs = post_request({"action": "get_blogs", "id": id_blog})
			self.accounts[str(id_blog)].blogs = blogs2list(newBlogs)
			for blog in self.accounts[str(id_blog)].blogs:
				self.write("\t\t    " + blog + "\n")
		elif table == "sb_tags":
			self.write("\t\tUpdate tags for '" + self.accounts[str(id_blog)].getAccountName() + "':\n")
			newTags = post_request({"action": "get_tags", "id": id_blog})
			self.accounts[str(id_blog)].tags = tags2list(newTags)
			for tag in self.accounts[str(id_blog)].tags:
				self.write("\t\t    " + tag + "\n")
		else:
			self.write("\t\tError: '" + table + "' is no a valid table!\n")


	def log(self, entry):
		if len(entry.split()) == 1:
			self.sbprog.logResults()
		else:
			try:
				if entry.split()[1] in ["all","All"]:
					for key, blog in self.accounts.iteritems():
						blog.logAccount()
				else:
					try:
						self.accounts[self.matches[entry.split()[1]]].logAccount()
					except KeyError, msg:
						self.write(entry.split()[1] + " is not an existing account!\n",True)
					
			except IndexError, msg:
				self.write("   Syntax error: 'log all' or 'log _blogname_'\n",True)


	def runBlogs(self, entry):
		try:
			if entry.split()[1] in ["all","All"]:
				for key, blog in self.accounts.iteritems():
					if blog.getAccountName() != "not available":
						blog.runBlog()
					else:
						self.write("Cannot run not available blog! (id: " + blog.strID + ")\n",True)
			else:
				try:
					self.accounts[self.matches[entry.split()[1]]].runBlog()
				except KeyError, msg:
					self.write(entry.split()[1] + " is not an existing account!\n",True)
			if self.canWrite:
				self.sbprog.logResults()
		except IndexError, msg:
			self.write("   Syntax error: 'run all' or 'run _blogname_'\n",True)


	def stopBlogs(self, entry):
		try:
			if entry.split()[1] in ["all","All"]:
				for kb,blog in self.accounts.iteritems():
					if blog.getAccountName() != "not available":
						blog.stopBlog()
				self.timers["update"].cancel()
				self.timers = {}
			else: 
				try:
					self.accounts[self.matches[entry.split()[1]]].stopBlog()
				except KeyError, msg:
					self.write(entry.split()[1] + " is not an existing blogname!\n",True)
		except IndexError, msg:
			self.write("   Syntax error: 'stop all' or 'stop _blogname_'\n",True)


	def setUpdateTimer(self):
		fiveMin = 60*5
		tup = threading.Timer(fiveMin, self.updateBlogs)
		tup.start()
		self.timers["update"] = tup
		deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + fiveMin)).strftime('%H:%M:%S %d/%m')
		self.timersTime["update"] = deadline


	def updateBlogs(self, firstTime=False):
		self.lock.acquire()
		self.writeln("Update blogs info..\n")
		self.write("Update social data:\n")
		for kb,blog in self.accounts.iteritems():
			blog.updateBlog()
		self.updateBlogsData(firstTime)
		self.synchOperations(firstTime)
		if not self.isTest:
			self.setUpdateTimer()
		self.updateStatistics(firstTime)
		self.lock.release()


	def closingOperations(self):
		for key, blog in self.accounts.iteritems():
			if blog.status == blog.STATUS_RUN:
				blog.stopBlog()

