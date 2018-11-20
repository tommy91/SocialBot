import time
import random
import datetime
import threading
import socket
from httplib2 import ServerNotFoundError

import Utils

class Account:

	STATUS_RUN = 1
	STATUS_STOP = 0

	TIMERHALFWINDOW = 10
	LIMITFOLLOW = 4950
	TIME_FACTOR = 1000000
	FOLLOWING_TRASH_TIME = 60*60*24*20		# 20 giorni
	FOLLOWERS_UPDATE_TIME = 60*60*24		# 1 giorno

	followersList = []
	followingList = []

	# account_type: 1 Tumblr, 2 Instagram


	def __init__(self, accounts, account_id, mail, account_type):
		print "Creating new Account object.."
		self.accounts = accounts
		self.output = accounts.output
		self.timers = accounts.sbprog.timers
		self.timersTime = accounts.sbprog.timersTime
		self.updateStatistics = accounts.sbprog.updateStatistics
		self.dbManager = accounts.sbprog.dbManager
		self.account_id = int(account_id)
		self.strID = str(account_id)
		self.mail = mail
		self.account_type = int(account_type)
		print "Account object created."


	def updateStatus(self):
		post_data_up = {"action": "get_my_accounts_ID", "id": self.account_id}
		status_res = post_request(post_data_up)
		if status_res != None:
			if (status_res[0]['State'] <= STATUS_RUN) and (self.status != status_res[0]['State']):
				post_request({"action": "set_status", "id": self.account_id, "status": self.status})


	def updateUpOp(self, newAccount):
		self.num_post_xd = int(newAccount['PostXD'])
		self.num_follow_xd = int(newAccount['FollowXD'])
		self.num_like_xd = int(newAccount['LikeXD'])
		self.num_post_xt = int(newAccount['PostXT'])
		self.num_follow_xt = int(newAccount['FollowXT'])
		self.num_like_xt = int(newAccount['LikeXT'])
		self.mail = newAccount['Mail']
		self.calc_time_post_follow()
		if int(newAccount['Status']) > self.STATUS_RUN:
			if self.status == self.STATUS_STOP:
				post_request({"action": "set_status", "id": self.account_id, "status": self.STATUS_RUN})
				self.runBlog()
			elif self.status == self.STATUS_RUN:
				post_request({"action": "set_status", "id": self.account_id, "status": self.STATUS_STOP})
				self.stopBlog()


	def runBlog(self):
		self.output.lock.acquire()
		prevCanWrite = self.canWrite
		self.canWrite = True
		self.output.writeln("Run " + self.getAccountName() + ":\n")
		self.calc_time_post_follow()
		self.checkData()
		self.updateBlog()
		if self.timers == {}:
			self.accounts.setUpdateTimer()
		self.initFollowers()
		self.initFollowings()
		self.set_post_timer()
		self.set_follow_timer()
		self.set_like_timer()
		self.output.write("\t" + self.getAccountName() + " is running.\n")
		self.status = self.STATUS_RUN
		self.updateBlogData()
		self.updateStatistics()
		self.canWrite = prevCanWrite
		self.output.lock.release()


	def stopBlog(self):
		self.output.lock.acquire()
		prevCanWrite = self.canWrite
		self.canWrite = True
		self.output.writeln("Stop " + self.getAccountName() + ".. \n")
		self.status = self.STATUS_STOP
		self.updateBlogData()
		self.timers[self.strID + "-post"].cancel()
		del self.timers[self.strID + "-post"]
		self.timers[self.strID + "-follow"].cancel()
		del self.timers[self.strID + "-follow"]
		self.timers[self.strID + "-like"].cancel()
		del self.timers[self.strID + "-like"]
		self.updateStatistics()
		self.output.write("\t" + self.getAccountName() + " stopped.\n")
		self.canWrite = prevCanWrite
		self.output.lock.release()


	def randomTag(self):
		new_tags = []
		for tag in self.tags:
			if not tag in ["follow4follow","follow","f4f","followback","Follow4Follow","Follow","F4F","FollowBack","like4like","like","likeback","l4l","Like4Like","Like","LikeBack","L4L"]:
				new_tags.append(tag)
		tag_pos = random.randint(0, len(new_tags)-1)
		return new_tags[tag_pos]


	def randomF4F(self):
		f4fs = ["follow4follow","follow","followback","f4f"]
		tag_pos = random.randint(0, len(f4fs)-1)
		return f4fs[tag_pos]


	def randomL4L(self):
		l4ls = ["like4like","like","likeback","l4l"]
		tag_pos = random.randint(0, len(l4ls)-1)
		return l4ls[tag_pos]


	def set_post_timer(self):
		timer_post = random.randint((self.timer_post) - (self.TIMERHALFWINDOW*60), (self.timer_post) + (self.TIMERHALFWINDOW*60))
		tp = threading.Timer(timer_post, self.post) # in seconds
		tp.start() 
		self.timers[self.strID + "-post"] = tp
		deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + timer_post)).strftime('%H:%M:%S %d/%m')
		self.timersTime[self.strID + "-post"] = deadline
		self.output.write("\tcreated new thread for post after " + seconds2timeStr(timer_post) + "\n")
		self.updateStatistics()


	def set_like_timer(self):
		timer_like = random.randint((self.timer_like) - (self.TIMERHALFWINDOW*60), (self.timer_like) + (self.TIMERHALFWINDOW*60))
		tl = threading.Timer(timer_like, self.like) # in seconds
		tl.start() 
		self.timers[self.strID + "-like"] = tl
		deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + timer_like)).strftime('%H:%M:%S %d/%m')
		self.timersTime[self.strID + "-like"] = deadline
		self.output.write("\tcreated new thread for like after " + seconds2timeStr(timer_like) + "\n")
		self.updateStatistics()


	def set_follow_timer(self):
		timer_follow = random.randint((self.timer_follow) - (self.TIMERHALFWINDOW*60), (self.timer_follow) + (self.TIMERHALFWINDOW*60))
		tf = threading.Timer(timer_follow, self.follow) # in seconds
		tf.start() 
		self.timers[self.strID + "-follow"] = tf
		deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + timer_follow)).strftime('%H:%M:%S %d/%m')
		self.timersTime[self.strID + "-follow"] = deadline
		self.output.write("\tcreated new thread for follow after " + seconds2timeStr(timer_follow) + "\n")
		self.updateStatistics()


	def checkData(self):
		bn = self.getAccountName()
		if bn != "not available":
			self.output.write("\tCheck data in DB for " + bn + ":\n")
			self.checkNeedNewPosts()
			self.checkNeedNewFollows()


	def checkNeedNewPosts(self):
		bn = self.getAccountName()
		# Check num Post
		posts = self.dbManager.countPost(bn)
		self.output.write("\t   check #post.. ")
		if posts >= self.num_post_xt:
			self.output.write("found " + str(posts) + ", ok\n")
		else:
			self.output.write("found " + str(posts) + ", needed at least " + str(self.num_post_xt) + "\n")
			self.search_post(num_post=(self.num_post_xt-posts))  


	def post(self, num_posts=-1, isDump = False):
		self.output.lock.acquire()
		blogname = self.getAccountName()
		self.output.writeln("Posting " + blogname + ":\n")
		if num_posts == -1:
			num_posts = self.num_post_xt
		posts = self.dbManager.getPosts(blogname,num_posts)
		if isDump:
			print posts 
		counter = 0
		for post in posts:
			try:
				if isDump:
					print post 
				self.postSocial(post)
				args = (post['id'],blogname)
				self.dbManager.delete("PostsLikes",args)
				counter += 1
				self.output.write("\r\tposted " + str(counter) + "/" + str(num_posts))
			except Exception,msg:
				self.output.write("\n\tError: exception on " + blogname + " reblogging\n" + str(msg) + "\n")
		self.output.write("\r\tposted " + str(counter) + " posts!\n")
		if not self.isTest:
			self.set_post_timer()
			self.checkNeedNewPosts()
		self.updateBlogData()
		self.output.lock.release()


	def follow(self, num_follows=-1, isDump = False):
		self.output.lock.acquire()
		blogname = self.getAccountName()
		self.output.writeln("Following " + blogname + ":\n")
		if num_follows == -1:
			num_follows = self.num_follow_xt
		# Check if need to update following
		self.checkFollowingStatus()
		self.followSocial(num_follows, isDump)
		if not self.accouns.sbprog.isTest:
			self.set_follow_timer()
			self.checkNeedNewFollows()
		self.updateBlogData()
		self.output.lock.release()


	def unfollow(self):
		blogname = self.getAccountName()
		self.output.writeln("Unfollowing " + blogname + ":\n")
		self.updateFollowers()
		counterUnfollow = 0
		while counterUnfollow <= self.num_follow_xt:
			try:
				# pop the first
				blog_name_unfollow = self.followingList.pop(0)
				if self.canUnfollow(blog_name_unfollow):
					# if can unfollow then unfollow
					self.unfollowSocial(blog_name_unfollow)
					args = (blogname, blog_name_unfollow)
					self.dbManager.delete("Following",args)
					counterUnfollow += 1
					self.output.write("\r\tUnfollowed " + str(counterUnfollow) + "/" + str(self.num_follow_xt))
				else:
					# else re-append at the end
					self.followingList.append(blog_name_unfollow)
			except IndexError, msg:
				self.output.write("Error: " + str(msg))
		self.output.write("\r\tUnfollowed " + str(counterUnfollow) + " blogs.\n")


	def canUnfollow(self):
		return True


	def like(self, num_likes=-1):
		blogname = self.getAccountName()
		self.output.lock.acquire()
		self.output.writeln("Liking " + blogname + ":\n")
		if num_likes == -1:
			num_likes = self.num_like_xt
		self.likeSocial(num_likes)
		if not isTest:
			self.set_like_timer()
		self.updateBlogData()
		self.output.lock.release()


	def checkFollowingStatus(self):
		if time.time >= self.updateFollowersTime:
			blogname = self.getAccountName()
			self.output.write("Time to update follower and following status..\n")
			# Get Followers
			self.getFollowers()
			# Update following status in db
			self.output.write("\tUpdate Following status.. ")
			self.dbManager.setAllFollowingUnfollowed(blogname)
			for follower in self.followersList:
				if follower in self.followingList:
					self.dbManager.setFollowingFollowed(blogname, follower, True)
			self.updateMatchesStatistics()
			self.followingList = self.dbManager.getFollowing(blogname)
			# Unfollow who did not follow me back after a while
			self.output.write("\tUnfollow who did not follow me back after a while.. ")
			timeLimit = int((time.time() - self.FOLLOWING_TRASH_TIME) * self.TIME_FACTOR)
			toUnfollow = self.dbManager.getFollowingTrash(blogname, timeLimit)
			self.output.write(str(len(toUnfollow)) + " to unfollow.. ")
			counterUnfollowed = 0
			for toUnfollowName in toUnfollow:
				try:
					self.unfollowSocial(toUnfollowName)
					self.followingList.remove(toUnfollowName)
					args = (blogname, toUnfollowName)
					self.dbManager.delete("Following",args)
					counterUnfollowed += 1
				except Exception, msg:
					self.output.write("\n\tError: exception on " + blogname + " unfollow for time!\n")
			self.output.write("unfollowed " + str(counterUnfollowed) + ".\n")
		# Check if too many follow and unfollow in that case
		if len(self.followingList) >= self.LIMITFOLLOW:
			try:
				self.unfollow()
			except Exception, msg:
				self.output.write("\n\tError: exception on " + blogname + " unfollow!\n")


	def initFollowings(self):
		self.output.write("Initialize Following.. ")
		self.followingList = []
		blogname = self.getAccountName()
		current_num_followings = self.dbManager.countFollowing(blogname)
		if current_num_followings != self.data['following']:
			self.dbManager.deleteAll("Following",blogname)
			self.getFollowing()
		else:
			self.followingList = self.dbManager.getFollowing(blogname)
		self.output.write("Done.\n")


	def initFollowers(self):
		self.output.write("Initialize Followers.. ")
		self.followersList = []
		self.getFollowers()
		self.output.write("Done.\n")


	def getFollowers(self):
		self.output.write("\tGet Followers List.. ")
		self.followersList = self.getFollowersSocial()
		self.updateFollowersTime = time.time() + self.FOLLOWERS_UPDATE_TIME


	def getFollowing(self):
		self.output.write("\tGet Following List.. ")
		self.followingList = []
		following = self.getFollowingsSocial()
		while following != []:
			follow = following.pop()
			if follow in followersList:
				args = (blogname, follow, True, int(time.time() * self.TIME_FACTOR))
			else:
				args = (blogname, follow, False, int(time.time() * self.TIME_FACTOR))
			self.dbManager.add("Following", args)
		self.followingList = self.dbManager.getFollowing(blogname)


	def clearDB(self):
		blogname = self.getAccountName()
		self.output.write("Clear DB tables for " + blogname + ".. ")
		self.dbManager.clearDB(blogname)
		self.output.write("done.\n")




