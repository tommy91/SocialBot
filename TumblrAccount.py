class TumblrAppAccount(Account):


	def __init__(self, account):
		super().__init__(account['ID'], account['Mail'], account['Type'])
		self.token = account['Token']
		self.token_secret = account['Token_Secret']



class TumbrlAccount(Account):


	client = None
	clientInfo = None
	followersList = []
    followingList = []


	def __init__(self, account, tags, blogs, app_accounts):
		super().__init__(account['ID'], account['Mail'], account['Type'])
		self.token = account['Token']
		self.token_secret = account['Token_Secret']
		self.app_account = app_accounts[str(account['App_Account'])]
		self.tags = tags2list(tags)
		self.blogs = blogs2list(blogs)
		self.data = self.get_blog_info()
		self.num_post_xd = int(account['PostXD'])
		self.num_follow_xd = int(account['FollowXD'])
		self.num_like_xd = int(account['LikeXD'])
		self.num_post_xt = int(account['PostXT'])
		self.num_follow_xt = int(account['FollowXT'])
		self.num_like_xt = int(account['LikeXT'])
		self.setup_clients()	
		status = self.STATUS_STOP


	def getAccountName(self):
		return self.data['blogname']

	
	def setup_clients(self):
	    self.client = pytumblr.TumblrRestClient(
	        self.app_account.token,
	        self.app_account.token_secret,
	        self.token,
	        self.token_secret,
	    )
	    self.clientInfo = pytumblr.TumblrRestClient(
	        self.app_account.token,
	        self.app_account.token_secret,
	        self.token,
	        self.token_secret,
	    )


	def get_blog_info(self):
	    cData = {'username': "not available",
	             'likes': "not available",
	             'following': "not available",
	             'followers': "not available",
	             'messages': "not available",
	             'blogname': "not available",
	             'posts': "not available",
	             'queue': "not available",
	             'url': "not available"
	             }
	    try:
	        response = self.client.info()
	        if self.checkResponse(response):
	            cData = {'username': response["user"]["name"],
	                     'likes': response["user"]["likes"],
	                     'following': response["user"]["following"],
	                     'followers': response["user"]["blogs"][0]["followers"],
	                     'messages': response["user"]["blogs"][0]["messages"],
	                     'blogname': response["user"]["blogs"][0]["name"],
	                     'posts': response["user"]["blogs"][0]["posts"],
	                     'queue': response["user"]["blogs"][0]["queue"],
	                     'url': response["user"]["blogs"][0]["url"]
	                     }
	    except ServerNotFoundError,msg:
	        write(str(msg) + "\n")
	    except socket.error, msg:
	        write(str(msg) + "\n")
	    return cData


	def checkResponse(self, res):
	    "Check if there is an error in response"
	    if "meta" in res:
	        write("Error: " + res["meta"]["msg"] + " (status " + str(res["meta"]["status"]) + ")\n")
	        return False
	    else:
	        return True


	def updateBlogData(self, timersTime):
	    write("\tUpdate " + self.data['blogname'] + ".. ")
	    post_data_up = {"action": "update_blog_data", 
	        "ID": self.account_id,
	        "Likes": self.data['likes'],
	        "Following": self.data['following'],
	        "Followers": self.data['followers'],
	        "Posts": self.data['posts'],
	        "Messages": self.data['messages'],
	        "Queue": self.data['queue'],
	        "Name": self.data['blogname'],
	        "Url": self.data['url']
	        }
	    if (self.strID + "-post") in timersTime:
	        post_data_up["Deadline_Post"] = timersTime[self.strID + "-post"]
	    if (self.strID + "-follow") in timersTime:
	        post_data_up["Deadline_Follow"] = timersTime[self.strID + "-follow"]
	    if (self.strID + "-like") in timersTime:
	        post_data_up["Deadline_Like"] = timersTime[self.strID + "-like"]
	    up_res = post_request(post_data_up)
	    if up_res != None:
	        self.updateStatus()
	        write("end of update.\n")


	def updateUpOp(self, newAccount, app_accounts):
		self.mail = newAccount['Mail']
		need_setup_clients = False 
		if self.app_account != app_accounts[str(newAccount['App_Account'])]:
			need_setup_clients = True 
        	self.app_account = app_accounts[str(newAccount['App_Account'])]
        if self.token != newAccount['Token']:
        	need_setup_clients = True
        	self.token = newAccount['Token']
        if self.token_secret != newAccount['Token_Secret']:
        	need_setup_clients = True
        	self.tokenSecret = newAccount['Token_Secret']
        if need_setup_clients:
            self.setup_clients()
        super().updateUpOp(newAccount)


