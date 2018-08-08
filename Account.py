import time
import random
import datetime
import threading
import socket
from pprint import pprint
from httplib2 import ServerNotFoundError

import Utils
import Output


class Account(object):

	STATUS_RUN = 1
	STATUS_STOP = 0

	TIMERFIRSTTIMEINTERVAL = 60
	TIMERHALFWINDOW = 10
	TIME_FACTOR = 1000000
	FOLLOWING_TRASH_TIME = 60*60*24*20		# 20 giorni
	FOLLOWERS_UPDATE_TIME = 60*60*24		# 1 giorno

	OVER_UNFOLLOW = 5

	followersList = []
	followingList = []

	todayPosts = 0
	todayLikes = 0
	todayFollows = 0
	todayUnfollows = 0


	def __init__(self, accounts, account_id, mail, account_type, username):
		self.accounts = accounts
		self.output = Output.Output(username + ".log")
		self.isTest = accounts.sbprog.isTest
		self.timers = accounts.sbprog.timers
		self.timersTime = accounts.sbprog.timersTime
		self.updateStatistics = accounts.sbprog.updateStatistics
		self.dbManager = accounts.sbprog.dbManager
		self.post_request = accounts.sbprog.post_request
		self.account_id = int(account_id)
		self.strID = str(account_id)
		self.mail = mail
		self.account_type = int(account_type)
		self.today = datetime.date.today()


	def updateStatus(self):
		post_data_up = {"action": "get_account_by_id", "id": self.account_id}
		status_res = self.post_request(post_data_up)
		if status_res != None:
			if self.status != status_res[0]['State']:
				self.post_request({"action": "set_status", "id": self.account_id, "status": self.status})


	def updateUpOp(self, newAccount):
		needCalcNewTimes = False
		if self.num_post_xd != int(newAccount['PostXD']):
			self.output.writeLog("\t\t    PostXD: " + str(self.num_post_xd) + " -> " + str(newAccount['PostXD']))
			self.num_post_xd = int(newAccount['PostXD'])
			needCalcNewTimes = True
		if self.num_follow_xd != int(newAccount['FollowXD']):
			self.output.writeLog("\t\t    FollowXD: " + str(self.num_follow_xd) + " -> " + str(newAccount['FollowXD']))
			self.num_follow_xd = int(newAccount['FollowXD'])
			needCalcNewTimes = True
		if self.num_like_xd != int(newAccount['LikeXD']):
			self.output.writeLog("\t\t    LikeXD: " + str(self.num_like_xd) + " -> " + str(newAccount['LikeXD']))
			self.num_like_xd = int(newAccount['LikeXD'])
			needCalcNewTimes = True
		if self.num_post_xt != int(newAccount['PostXT']):
			self.output.writeLog("\t\t    PostXT: " + str(self.num_post_xt) + " -> " + str(newAccount['PostXT']))
			self.num_post_xt = int(newAccount['PostXT'])
			needCalcNewTimes = True
		if self.num_follow_xt != int(newAccount['FollowXT']):
			self.output.writeLog("\t\t    FollowXT: " + str(self.num_follow_xt) + " -> " + str(newAccount['FollowXT']))
			self.num_follow_xt = int(newAccount['FollowXT'])
			needCalcNewTimes = True
		if self.num_like_xt != int(newAccount['LikeXT']):
			self.output.writeLog("\t\t    LikeXT: " + str(self.num_like_xt) + " -> " + str(newAccount['LikeXT']))
			self.num_like_xt = int(newAccount['LikeXT'])
			needCalcNewTimes = True
		if self.mail != newAccount['Mail']:
			self.output.writeLog("\t\t    Mail: " + self.mail + " -> " + newAccount['Mail'])
			self.mail != newAccount['Mail']
		if needCalcNewTimes:
			self.output.writeLog("\t\t    Setup new timers.. ")
			self.calc_time_post_follow()
			self.output.writeLog("ok")
		else:
			self.output.writeLog("\t\t    No need to setup new timers!\n")
		if int(newAccount['State']) > self.STATUS_RUN:
			if self.status == self.STATUS_STOP:
				self.output.writeLog("\t\t    Need to run the blog:\n")
				self.post_request({"action": "set_status", "id": self.account_id, "status": self.STATUS_RUN})
				self.runBlog()
			elif self.status == self.STATUS_RUN:
				self.output.writeLog("\t\t    Need to stop the blog:\n")
				self.post_request({"action": "set_status", "id": self.account_id, "status": self.STATUS_STOP})
				self.stopBlog()
		else:
			self.output.writeLog("\t\t    No need to change the status of the blog!\n")


	def runBlog(self):
		self.init_tread = threading.Thread(name=self.getAccountName() + "_init_thread", target=self.initRun)
		self.init_tread.start()


	def initRun(self):
		self.output.writeLog("Run " + self.getAccountName() + "on thread '" + self.init_tread.getName() + "'" + ":\n")
		self.calc_time_post_follow()
		self.checkData()
		self.updateAccount()
		if self.timers == {}:
			self.accounts.setUpdateTimer()
		self.initFollowers()
		self.initFollowings()
		self.setTimers(firstTime=True)
		self.output.writeLog("\t" + self.getAccountName() + " is running.\n")
		self.status = self.STATUS_RUN
		self.updateAccountData()
		self.updateStatistics()
		self.output.writeLog("\tThread '" + self.init_tread.getName() + "' is done.\n")


	def stopBlog(self):
		self.output.writeLog("Stop " + self.getAccountName() + ".. \n")
		if self.init_tread.isAlive():
			self.output.writeLog("\tWaiting thread '" + self.init_tread.getName() + "' to stop..\n")
			self.init_tread.join()
		self.status = self.STATUS_STOP
		self.updateBlogData()
		self.stopTimers()
		self.updateStatistics()
		self.output.writeLog("\t" + self.getAccountName() + " stopped.\n")


	def selectTag(self):
		new_tags = []
		tags_names = self.tags.keys()
		if len(tags_names) == 0:
			return ""
		sum_used_tags = 0.0
		for tag_name in tags_names:
			sum_used_tags += float(self.tags[tag_name]['Success']) / self.tags[tag_name]['Used']
		tags_probs = [ self.tags[tn]['Success'] / ( self.tags[tn]['Used'] * sum_used_tags ) for tn in tags_names ]
		return Utils.selectWithProb(tags_names, tags_probs)


	def setTimers(self, firstTime=False):
		if self.timer_post > 0:
			self.set_post_timer(firstTime)
			self.isPosting = True
		else:
			self.isPosting = False
		if self.timer_follow > 0:
			self.set_follow_timer(firstTime)
			self.isFollowing = True
		else:
			self.isFollowing = False
		if self.timer_like > 0:
			self.set_like_timer(firstTime)
			self.isLiking = True
		else:
			self.isLiking = False


	def stopTimers(self):
		if self.isPosting:
			self.timers[self.strID + "-post"].cancel()
			del self.timers[self.strID + "-post"]
		if self.isFollowing:
			self.timers[self.strID + "-follow"].cancel()
			del self.timers[self.strID + "-follow"]
		if self.isLiking:
			self.timers[self.strID + "-like"].cancel()
			del self.timers[self.strID + "-like"]


	def set_post_timer(self, firstTime=False):
		if firstTime:
			timer_post = self.TIMERFIRSTTIMEINTERVAL
		else:
			timer_post = random.randint((self.timer_post) - (self.TIMERHALFWINDOW*60), (self.timer_post) + (self.TIMERHALFWINDOW*60))
		tp = threading.Timer(timer_post, self.post) # in seconds
		tp.start() 
		self.timers[self.strID + "-post"] = tp
		deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + timer_post)).strftime('%H:%M:%S %d/%m')
		self.timersTime[self.strID + "-post"] = deadline
		self.output.writeLog("\tcreated new thread for post after " + Utils.seconds2timeStr(timer_post) + "\n")
		self.updateStatistics()


	def set_like_timer(self, firstTime=False):
		if firstTime:
			timer_like = self.TIMERFIRSTTIMEINTERVAL * 2
		else:
			timer_like = random.randint((self.timer_like) - (self.TIMERHALFWINDOW*60), (self.timer_like) + (self.TIMERHALFWINDOW*60))
		tl = threading.Timer(timer_like, self.like) # in seconds
		tl.start() 
		self.timers[self.strID + "-like"] = tl
		deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + timer_like)).strftime('%H:%M:%S %d/%m')
		self.timersTime[self.strID + "-like"] = deadline
		self.output.writeLog("\tcreated new thread for like after " + Utils.seconds2timeStr(timer_like) + "\n")
		self.updateStatistics()


	def set_follow_timer(self, firstTime=False):
		if firstTime:
			timer_follow = self.TIMERFIRSTTIMEINTERVAL * 3
		else:
			timer_follow = random.randint((self.timer_follow) - (self.TIMERHALFWINDOW*60), (self.timer_follow) + (self.TIMERHALFWINDOW*60))
		tf = threading.Timer(timer_follow, self.follow) # in seconds
		tf.start() 
		self.timers[self.strID + "-follow"] = tf
		deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + timer_follow)).strftime('%H:%M:%S %d/%m')
		self.timersTime[self.strID + "-follow"] = deadline
		self.output.writeLog("\tcreated new thread for follow after " + Utils.seconds2timeStr(timer_follow) + "\n")
		self.updateStatistics()


	def checkData(self):
		bn = self.getAccountName()
		if bn != "not available":
			self.output.writeLog("\tCheck data in DB for " + bn + ":\n")
			self.checkNeedNewPosts()
			self.checkNeedNewFollows()


	def checkNeedNewPosts(self):
		bn = self.getAccountName()
		# Check num Post
		posts = self.dbManager.countPost(bn)
		self.output.writeLog("\t   check #post.. needed " + str(self.num_post_xt) + ".. \n")
		if posts >= self.num_post_xt:
			self.output.writeLog("\t\tfound " + str(posts) + ", ok\n")
		else:
			self.output.writeLog("\t\tfound " + str(posts) + ", needed at least " + str(self.num_post_xt) + "\n")
			self.search_post(num_post=(self.num_post_xt-posts))  


	def post(self, num_posts = -1, isDump = False):
		blogname = self.getAccountName()
		if not self.isTest:
			self.set_post_timer()
		self.output.writeLog("Posting " + blogname + ":\n")
		if num_posts == -1:
			num_posts = self.num_post_xt
		posts = self.dbManager.getPosts(blogname,num_posts)
		if isDump:
			self.output.writeLog(str(posts) + "\n") 
		counter = 0
		for post in posts:
			try:
				if isDump:
					self.output.writeLog(str(post) + "\n") 
				self.postSocial(post)
				args = (post['id'],blogname)
				self.dbManager.delete("PostsLikes",args)
				counter += 1
				self.output.writeLog("\tposted " + str(counter) + "/" + str(num_posts) + "\n")
			except Exception,msg:
				self.output.writeErrorLog("\tError: exception on " + blogname + " reblogging\n" + str(msg) + "\n")
		self.output.writeLog("\tposted " + str(counter) + " posts!\n")
		if not self.isTest:
			self.checkNeedNewPosts()
		self.updateBlogData()


	def follow(self, num_follows = -1, isDump = False):
		blogname = self.getAccountName()
		if not self.isTest:
			self.set_follow_timer()
		self.output.writeLog("Following " + blogname + ":\n")
		if num_follows == -1:
			num_follows = self.num_follow_xt
		# Check if need to update following
		self.checkFollowingStatus()
		self.followSocial(num_follows, isDump)
		if not self.isTest:
			self.checkNeedNewFollows()
		self.updateBlogData()


	def unfollow(self):
		blogname = self.getAccountName()
		self.output.writeLog("Unfollowing " + blogname + ":\n")
		counterUnfollow = 0
		while counterUnfollow <= self.num_follow_xt + self.OVER_UNFOLLOW:
			try:
				# pop the first
				blog_name_unfollow = self.followingList.pop(0)
				if self.canUnfollow(blog_name_unfollow):
					# if can unfollow then unfollow
					self.unfollowSocial(blog_name_unfollow)
					args = (blogname, blog_name_unfollow)
					self.dbManager.delete("Following",args)
					counterUnfollow += 1
					self.output.writeLog("\tUnfollowed " + str(counterUnfollow) + "/" + str(self.num_follow_xt) + "\n")
				else:
					# else re-append at the end
					self.followingList.append(blog_name_unfollow)
			except IndexError, msg:
				self.output.writeErrorLog("\tError: " + str(msg) + "\n")
			except Exception, msg:
				self.output.writeErrorLog("\tError: exception on " + blogname + " unfollow!" + "\n")
		self.output.writeLog("\tUnfollowed " + str(counterUnfollow) + " blogs.\n")


	def canUnfollow(self,blog2unfollow):
		return True


	def like(self, num_likes = -1, isDump = False):
		blogname = self.getAccountName()
		if not self.isTest:
			self.set_like_timer()
		self.output.writeLog("Liking " + blogname + ":\n")
		if num_likes == -1:
			num_likes = self.num_like_xt
		self.likeSocial(num_likes, isDump)
		self.updateBlogData()


	def checkFollowingStatus(self):
		blogname = self.getAccountName()
		if time.time() >= self.updateFollowersTime:
			self.output.writeLog("Time to update follower and following status..\n")
			# Get Followers
			self.getFollowers()
			# Update following status in db
			self.output.writeLog("\tUpdate Following status.. \n")
			self.dbManager.setAllFollowingUnfollowed(blogname)
			for follower in self.followersList:
				if follower in self.followingList:
					self.dbManager.setFollowingFollowed(blogname, follower, True)
			self.updateMatchesStatistics()
			self.followingList = self.dbManager.getFollowing(blogname)
			# Unfollow who did not follow me back after a while
			self.output.writeLog("\tUnfollow who did not follow me back after a while.. ")
			timeLimit = int((time.time() - self.FOLLOWING_TRASH_TIME) * self.TIME_FACTOR)
			toUnfollow = self.dbManager.getFollowingTrash(blogname, timeLimit)
			self.output.writeLog(str(len(toUnfollow)) + " to unfollow.. ")
			counterUnfollowed = 0
			for toUnfollowName in toUnfollow:
				try:
					self.unfollowSocial(toUnfollowName)
					self.followingList.remove(toUnfollowName)
					args = (blogname, toUnfollowName)
					self.dbManager.delete("Following",args)
					counterUnfollowed += 1
				except Exception, msg:
					self.output.writeErrorLog("\tError: exception on " + blogname + " unfollow for time!\n")
			self.output.writeLog("unfollowed " + str(counterUnfollowed) + ".\n")
		# Check if too many follow and unfollow in that case
		if len(self.followingList) >= self.LIMITFOLLOW:
			self.output.writeLog("\t#Following: " + str(len(self.followingList)) + " >= max # following (" + str(self.LIMITFOLLOW) + ") -> need to unfollow!\n")
			self.unfollow()
		else:
			self.output.writeLog("\t#Following: " + str(len(self.followingList)) + " < max # following (" + str(self.LIMITFOLLOW) + ") -> NO need to unfollow!\n")
			


	def initFollowings(self):
		self.output.writeLog("\tInitialize Following.. \n")
		self.followingList = []
		blogname = self.getAccountName()
		current_num_followings = self.dbManager.countFollowing(blogname)
		if current_num_followings != self.data['following']:
			following = self.getFollowing()
		else:
			self.output.writeLog("\t\tGet Following List from DB.. ")
			following = self.dbManager.getFollowing(blogname)
			self.output.writeLog("ok\n")
		args = (blogname,)
		self.dbManager.deleteAll("Following",args)
		self.checkFollowingFollowed(following)
		self.output.writeLog("\tDone.\n")


	def initFollowers(self):
		self.output.writeLog("\tInitialize Followers.. ")
		self.followersList = []
		self.getFollowers()
		self.orderedFollowersList = sorted(self.followersList)
		self.output.writeLog("\tDone.\n")


	def getFollowers(self):
		self.output.writeLog("\t\tGet Followers List.. \n")
		self.followersList = self.getFollowersSocial()
		self.updateFollowersTime = time.time() + self.FOLLOWERS_UPDATE_TIME


	def getFollowing(self):
		self.output.writeLog("\t\tGet Following List.. \n")
		return self.getFollowingsSocial()


	def checkFollowingFollowed(self, following): 
		blogname = self.getAccountName()
		counter = 0
		count_final_str = str(len(following))
		following2insert = []
		while following != []:
			follow = following.pop()
			counter += 1
			self.output.writeLog("\t\tCheck following " + str(counter) + "/" + count_final_str + "\n")
			if Utils.binarySearch(follow, self.orderedFollowersList):
				args = (blogname, follow, True, int(time.time() * self.TIME_FACTOR))
			else:
				args = (blogname, follow, False, int(time.time() * self.TIME_FACTOR))
			following2insert.append(args)
		self.output.writeLog("\t\tInsert following in DB.. ")
		self.dbManager.addList("Following", following2insert)
		self.output.writeLog("ok!\n")
		self.followingList = self.dbManager.getFollowing(blogname)


	def clearDB(self):
		blogname = self.getAccountName()
		self.output.writeLog("Clear DB tables for " + blogname + ".. ")
		self.dbManager.clearDB(blogname)
		self.output.writeLog("done.\n")




