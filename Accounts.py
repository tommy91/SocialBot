import Utils

class Accounts:

	TYPE_TUMBLR = 1
	TYPE_INSTAGRAM = 2

	def __init__(self, sbprog):
		self.app_accounts = {}
		self.accounts = {}
		self.matches = {}
		self.timersTime = {}
		self.output = output
		self.write = self.sbprog.output.write
		self.writeln = self.sbprog.output.writeln
		self.initAccounts()
		self.updateBlogsData(firstTime=True)
		self.synchOperations(firstTime=True)


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
	            self.addMyAccount(myAccount,tags,otherAccounts)
	            counter = counter + 1
	            self.write("Done!\n")


	def addAppAccount(self, account):
		self.app_accounts{str(account['ID']): TumblrAppAccount(account)}


	def addAccount(self, account, tags, blogs):
		if account['Type'] == self.TYPE_TUMBLR:
			new_account = TumblrAccount(account, tags, blogs, self.app_accounts) 
		elif account['Type'] == self.TYPE_INSTAGRAM:
			new_account = InstagramAccount(account, tags, blogs)
		else:
			self.write("Error at addAccount for account " + str(account['Mail']))
			return
		self.accounts{str(account['ID']): new_account}
		account_name = new_account.getAccountName()
		if account_name != "not available":
        	self.matches[account_name] = account['ID']}


	def updateBlogsData(self, firstTime=False):
	    if firstTime:
	        self.write("Update Blogs:\n")
	    else: 
	        self.writeln("Update Blogs:\n")
	    for key, blog in self.accounts.iteritems():
	        blog.updateBlogData(self.timersTime)


	def synchOperations(self, firstTime=False):
	    if firstTime:
	        self.write("Synchronize with online register.. ")
	    else:
	        self.write("\tSynchronize with online register.. ")
	    synch_req = post_request({'action': "synch_operations"})
	    if len(synch_req) > 0:
	        self.write("\n")
	        for up_row in synch_req:
	            self.updateData(up_row)
	    else:
	        self.write("already synch!\n")


	def updateData(self, row):
	    if row['Operation'] == '0':
	        self.updateAddOp(row['Table'],row['Blog'])
	    elif row['Operation'] == '1':
	        self.updateDelOp(row['Table'],row['Blog'])
	    elif row['Operation'] == '2':
	        self.updateUpOp(row['Table'],row['Blog'])
	    else:
	        self.write("\t\tError: operation " + str(row['Operation']) + "unknown!\n")


	def updateAddOp(self, table, id_blog):
	    if table == "sb_app_accounts":
	        newAppAccount = post_request({"action": "get_app_accounts_ID", "id": id_blog})
	        self.addAppAccount(newAppAccount)
	    elif table == "sb_my_accounts":
	        newMyAccount = post_request({"action": "get_my_accounts_ID", "id": id_blog})
	        newTags = post_request({"action": "get_tags", "id": id_blog})
	        newBlogs = post_request({"action": "get_blogs", "id": id_blog})
	        self.addAccount(newMyAccount, newTags, newBlogs)
	        if newMyAccount['status'] == self.STATUS_RUN:
	            self.accounts[str(id_blog)].runBlog()
	    elif table == "sb_other_accounts":
	        newBlogs = post_request({"action": "get_blogs", "id": id_blog})
	        self.accounts[str(id_blog)].blogs = blogs2list(newBlogs)
	    elif table == "sb_tags":
	        newTags = post_request({"action": "get_tags", "id": id_blog})
	        self.accounts[str(id_blog)].tags = tags2list(newTags)
	    else:
	        self.write("\t\tError: '" + table + "' is no a valid table!")


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
	        del self.matches[self.accounts[str(id_blog)].getAccountName()]
	        del self.accounts[str(id_blog)]
	        # todo cancellare tabelle db locale per account
	    elif table == "sb_other_accounts":
	        newBlogs = post_request({"action": "get_blogs", "id": id_blog})
	        self.accounts[str(id_blog)].blogs = blogs2list(newBlogs)
	    elif table == "sb_tags":
	        newTags = post_request({"action": "get_tags", "id": id_blog})
	        self.accounts[str(id_blog)].tags = tags2list(newTags)
	    else:
	        self.write("\t\tError: '" + table + "' is no a valid table!")


	def updateUpOp(self, table, id_blog):
	    if table == "sb_app_accounts":
	        newAppAccount = post_request({"action": "get_app_accounts_ID", "id": id_blog})
	        self.addAppAccount(newAppAccount)
	    elif table == "sb_my_accounts":
	    	newAccount = post_request({"action": "get_my_accounts_ID", "id": id_blog})
	    	self.accounts[str(id_blog)].updateUpOp(newAccount, app_accounts)
	    elif (table == "sb_other_accounts") or (table == "sb_tags"):
	        self.write("\t\tOperation not permitted!!! WTF is happening???")
	    else:
	        self.write("\t\tError: '" + table + "' is no a valid table!")

