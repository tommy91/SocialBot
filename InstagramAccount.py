class InstagramAccount(Account):


	followersList = []
    followingList = []


	def __init__(self, account, tags, blogs):
		super().__init__(account['ID'], account['Mail'], account['Type'])
		self.username = account['Username']
		self.password = account['Password']
		self.tags = tags2list(tags)
		self.blogs = blogs2list(blogs)
		self.data = self.get_blog_info()
		self.num_post_xd = int(account['PostXD'])
		self.num_follow_xd = int(account['FollowXD'])
		self.num_like_xd = int(account['LikeXD'])
		self.num_post_xt = int(account['PostXT'])
		self.num_follow_xt = int(account['FollowXT'])
		self.num_like_xt = int(account['LikeXT'])
		status = self.STATUS_STOP


	def getAccountName(self):
		return self.data['name']


	def get_blog_info(self):
	    ibi = post_request({'action': 'get_insta_blog_info', 'username': self.username, 'password': self.password})
	    if ibi != None:
	        return {'private': ibi['private'],
	                'following': ibi['following'],
	                'followers': ibi['follower'],
	                'messages': ibi['message'],
	                'name': ibi['name'],
	                'posts': ibi['post'],
	                'usertags': ibi['usertags']
	                }
	    else:
	        return {'private': "not available",
	                'following': "not available",
	                'followers': "not available",
	                'messages': "not available",
	                'name': "not available",
	                'posts': "not available",
	                'usertags': "not available"
	                }


	def updateBlogData(self, timersTime):
	    write("\tUpdate " + self.data['name'] + ".. ")
	    post_data_up = {"action": "update_blog_data_insta", 
	        "ID": self.account_id,
	        "Following": self.data['following'],
	        "Followers": self.data['followers'],
	        "Posts": self.data['posts'],
	        "Messages": self.data['messages'],
	        "Name": self.data['name'],
	        "Private": self.data['private'],
	        "Usertags": self.data['usertags']
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
        self.username = newAccount['Username']
        self.password = newAccount['Password']
        super().updateUpOp(newAccount)






