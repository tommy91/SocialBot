import Utils

import Account
import TumblrAccount
import InstagramAccount

class Accounts:

	TYPE_TUMBLR = 1
	TYPE_INSTAGRAM = 2

	def __init__(self, sbprog):
		print "Creating new Accounts object.."
		self.instagramAccounts = {}
		self.matches = {}
		self.timersTime = sbprog.timersTime
		self.timers = sbprog.timers
		self.output = sbprog.output
		self.updateStatistics = sbprog.updateStatistics
		self.initAccounts()
		self.updateAccounts()
		self.updateBlogsData(firstTime=True)
		self.synchOperations(firstTime=True)
		print "Accounts object created."


	def initAccounts(self):
		self.initInstagramAccounts()
		

	def initInstagramAccounts(self):
		self.output.write("Get Instagram Accounts.. ")
		instagramAccounts = Utils.post_request({"action": "get_instagram_accounts"})
		if instagramAccounts == None:
			print "\tError: None response."
			return
		print "ok"
		print "Instagram Accounts:"
		if len(instagramAccounts) == 0:
			print "\tNo accounts fonud."
		else:
			counter = 1
			for instaAccount in instagramAccounts:
				print "\t" + str(counter) + ") " + instaAccount["Mail"]
				counter += 1
			print "Get Accounts Data:"
			counter = 1
			for instaAccount in instagramAccounts:
				self.output.write("\t" + str(counter) + ") " + instaAccount["Mail"] + " -> tags.. ")
				tags = Utils.post_request({"action": "get_tags", "ID": instaAccount['ID']})
				self.output.write(" otherAccounts.. ")
				blogs = Utils.post_request({"action": "get_blogs", "ID": instaAccount['ID']})
				if (tags == None) or (blogs == None):
					# error in response
					continue
				self.output.write("add account.. ")
				self.addInstagramAccount(instaAccount,tags,blogs)
				counter += 1
				print "Done!"


	def addInstagramAccount(self, account, tags, blogs):
		new_insta_account = InstagramAccount.InstagramAccount(self, account, tags, blogs)
		self.instagramAccounts[str(account['ID'])] = new_insta_account
		self.matches[account['Name']] = account['ID']


	def updateBlogsData(self, firstTime=False):
		if firstTime:
			self.output.write("Update Blogs:\n")
		else: 
			self.output.writeln("Update Blogs:\n")
		for key, blog in self.accounts.iteritems():
			blog.updateBlogData(self.timersTime)


	def synchOperations(self, firstTime=False):
		if firstTime:
			self.output.write("Synchronize with online register.. ")
		else:
			self.output.write("\tSynchronize with online register.. ")
		synch_req = Utils.post_request({'action': "synch_operations"})
		if len(synch_req) > 0:
			self.output.write("\n")
			for up_row in synch_req:
				self.updateData(up_row)
		else:
			self.output.write("already synch!\n")


	def updateData(self, row):
		if row['Operation'] == '0':
			self.updateAddOp(row['Table'],row['Blog'])
		elif row['Operation'] == '1':
			self.updateDelOp(row['Table'],row['Blog'])
		elif row['Operation'] == '2':
			self.updateUpOp(row['Table'],row['Blog'])
		else:
			self.output.write("\t\tError: operation " + str(row['Operation']) + "unknown!\n")


	def updateAddOp(self, table, id_blog):
		if table == "sb_app_accounts":
			newAppAccount = Utils.post_request({"action": "get_app_accounts_ID", "id": id_blog})
			self.addAppAccount(newAppAccount)
		elif table == "sb_my_accounts":
			newMyAccount = Utils.post_request({"action": "get_my_accounts_ID", "id": id_blog})
			newTags = Utils.post_request({"action": "get_tags", "id": id_blog})
			newBlogs = Utils.post_request({"action": "get_blogs", "id": id_blog})
			self.addAccount(newMyAccount, newTags, newBlogs)
			if newMyAccount['status'] == self.STATUS_RUN:
				self.accounts[str(id_blog)].runBlog()
		elif table == "sb_other_accounts":
			newBlogs = Utils.post_request({"action": "get_blogs", "id": id_blog})
			self.accounts[str(id_blog)].blogs = blogs2list(newBlogs)
		elif table == "sb_tags":
			newTags = Utils.post_request({"action": "get_tags", "id": id_blog})
			self.accounts[str(id_blog)].tags = tags2list(newTags)
		else:
			self.output.write("\t\tError: '" + table + "' is no a valid table!")


	def updateDelOp(self, table, id_blog):
		if table == "sb_app_accounts":
			for key, blog in self.accounts:
				if blog.app_account == id_blog:
					self.accounts[key].app_account = None
					self.accounts[key].client = None
					self.accounts[key].clientInfo = None
			del self.app_accounts[str(id_blog)]
		elif table == "sb_my_accounts":
			if self.accounts[str(id_blog)].status == self.STATUS_RUN:
				self.accounts[str(id_blog)].stopBlog()
				self.accounts[str(id_blog)].clearDB()
			del self.matches[self.accounts[str(id_blog)].getAccountName()]
			del self.accounts[str(id_blog)]
		elif table == "sb_other_accounts":
			newBlogs = Utils.post_request({"action": "get_blogs", "id": id_blog})
			self.accounts[str(id_blog)].blogs = blogs2list(newBlogs)
		elif table == "sb_tags":
			newTags = Utils.post_request({"action": "get_tags", "id": id_blog})
			self.accounts[str(id_blog)].tags = tags2list(newTags)
		else:
			self.output.write("\t\tError: '" + table + "' is no a valid table!")


	def updateUpOp(self, table, id_blog):
		if table == "sb_app_accounts":
			newAppAccount = Utils.post_request({"action": "get_app_accounts_ID", "id": id_blog})
			self.addAppAccount(newAppAccount)
		elif table == "sb_my_accounts":
			newAccount = Utils.post_request({"action": "get_my_accounts_ID", "id": id_blog})
			self.accounts[str(id_blog)].updateUpOp(newAccount)
		elif (table == "sb_other_accounts") or (table == "sb_tags"):
			self.output.write("\t\tOperation not permitted!!! WTF is happening???")
		else:
			self.output.write("\t\tError: '" + table + "' is no a valid table!")


	def runBlogs(self, entry):
		try:
			if entry.split()[1] in ["all","All"]:
				for key, blog in self.accounts.iteritems():
					if blog.getAccountName() != "not available":
						blog.runBlog()
					else:
						self.output.write("Cannot run not available blog! (id: " + blog.strID + ")\n",True)
			else:
				try:
					self.accounts[matches[entry.split()[1]]].runBlog()
				except KeyError, msg:
					self.output.write(entry.split()[1] + " is not an existing account!\n",True)
			if self.canWrite:
				self.logResults()
		except IndexError, msg:
			self.output.write("   Syntax error: 'run all' or 'run _blogname_'\n",True)


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
					self.accounts[matches[entry.split()[1]]].stopBlog()
				except KeyError, msg:
					self.output.write(entry.split()[1] + " is not an existing blogname!\n",True)
		except IndexError, msg:
			self.output.write("   Syntax error: 'stop all' or 'stop _blogname_'\n",True)


	def setUpdateTimer(self):
		fiveMin = 60*5
		tup = threading.Timer(fiveMin, self.updateBlogs)
		tup.start()
		self.timers["update"] = tup
		deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + fiveMin)).strftime('%H:%M:%S %d/%m')
		self.timersTime["update"] = deadline


	#def updateBlogs(self):
	def updateAccounts(self):
		self.output.lock.acquire()
		self.output.writeln("Update blogs info.\n")
		# Update Instagram Accounts
		for kb,blog in self.instagramAccounts.iteritems():
			blog.updateAccount()
		self.updateBlogsData()
		self.synchOperations()
		self.updateStatistics()
		if not self.isTest:
			self.setUpdateTimer()
		self.output.lock.release()


	def closingOperations(self):
		for key, blog in self.accounts.iteritems():
			if blog.status == blog.STATUS_RUN:
				blog.stopBlog()

