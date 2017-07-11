import time
import random
import datetime
import threading
import socket
from pprint import pprint
from httplib2 import ServerNotFoundError

from Utils import *
from Output import Output


class Account(object):

	STATUS_RUN = 1
	STATUS_STOP = 0

	TIMERHALFWINDOW = 10
	TIME_FACTOR = 1000000
	FOLLOWING_TRASH_TIME = 60*60*24*20		# 20 giorni
	FOLLOWERS_UPDATE_TIME = 60*60*24		# 1 giorno

	followersList = []
	followingList = []

	notGoodTags = ["follow4follow","follow","f4f","followback","Follow4Follow","Follow","F4F","FollowBack","like4like","like","likeback","l4l","Like4Like","Like","LikeBack","L4L"]


	def __init__(self, accounts, account_id, mail, account_type):
		self.accounts = accounts
		self.isTest = accounts.sbprog.isTest
		self.output = Output(mail + ".log")
		self.write = self.output.write
		self.writeError = self.output.writeError
		self.timers = accounts.sbprog.timers
		self.timersTime = accounts.sbprog.timersTime
		self.updateStatistics = accounts.sbprog.updateStatistics
		self.dbManager = accounts.sbprog.dbManager
		self.post_request = accounts.sbprog.post_request
		self.account_id = int(account_id)
		self.strID = str(account_id)
		self.mail = mail
		self.account_type = int(account_type)


	def updateStatus(self):
		post_data_up = {"action": "get_my_accounts_ID", "id": self.account_id}
		status_res = self.post_request(post_data_up)
		if status_res != None:
			if self.status != status_res[0]['State']:
				self.post_request({"action": "set_status", "id": self.account_id, "status": self.status})


	def updateUpOp(self, newAccount):
		needCalcNewTimes = False
		if self.num_post_xd != int(newAccount['PostXD']):
			self.write("\t\t    PostXD: " + str(self.num_post_xd) + " -> " + str(newAccount['PostXD']))
			self.num_post_xd = int(newAccount['PostXD'])
			needCalcNewTimes = True
		if self.num_follow_xd != int(newAccount['FollowXD']):
			self.write("\t\t    FollowXD: " + str(self.num_follow_xd) + " -> " + str(newAccount['FollowXD']))
			self.num_follow_xd = int(newAccount['FollowXD'])
			needCalcNewTimes = True
		if self.num_like_xd != int(newAccount['LikeXD']):
			self.write("\t\t    LikeXD: " + str(self.num_like_xd) + " -> " + str(newAccount['LikeXD']))
			self.num_like_xd = int(newAccount['LikeXD'])
			needCalcNewTimes = True
		if self.num_post_xt != int(newAccount['PostXT']):
			self.write("\t\t    PostXT: " + str(self.num_post_xt) + " -> " + str(newAccount['PostXT']))
			self.num_post_xt = int(newAccount['PostXT'])
			needCalcNewTimes = True
		if self.num_follow_xt != int(newAccount['FollowXT']):
			self.write("\t\t    FollowXT: " + str(self.num_follow_xt) + " -> " + str(newAccount['FollowXT']))
			self.num_follow_xt = int(newAccount['FollowXT'])
			needCalcNewTimes = True
		if self.num_like_xt != int(newAccount['LikeXT']):
			self.write("\t\t    LikeXT: " + str(self.num_like_xt) + " -> " + str(newAccount['LikeXT']))
			self.num_like_xt = int(newAccount['LikeXT'])
			needCalcNewTimes = True
		if self.mail != newAccount['Mail']:
			self.write("\t\t    Mail: " + self.mail + " -> " + newAccount['Mail'])
			self.mail != newAccount['Mail']
		if needCalcNewTimes:
			self.write("\t\t    Setup new timers.. ")
			self.calc_time_post_follow()
			self.write("ok")
		else:
			self.write("\t\t    No need to setup new timers!")
		if int(newAccount['State']) > self.STATUS_RUN:
			if self.status == self.STATUS_STOP:
				self.write("\t\t    Need to run the blog:")
				self.post_request({"action": "set_status", "id": self.account_id, "status": self.STATUS_RUN})
				self.runBlog()
			elif self.status == self.STATUS_RUN:
				self.write("\t\t    Need to stop the blog:")
				self.post_request({"action": "set_status", "id": self.account_id, "status": self.STATUS_STOP})
				self.stopBlog()
		else:
			self.write("\t\t    No need to change the status of the blog!")


	def runBlog(self):
		self.init_tread = threading.Thread(name=self.getAccountName() + "_init_thread", target=self.initRun)
		self.init_tread.start()


	def initRun(self):
		self.write("Run " + self.getAccountName() + "on thread '" + self.init_tread.getName() + "'" + ":")
		self.calc_time_post_follow()
		self.checkData()
		self.updateBlog()
		if self.timers == {}:
			self.accounts.setUpdateTimer()
		self.initFollowers()
		self.initFollowings()
		self.setTimers()
		self.write("\t" + self.getAccountName() + " is running.")
		self.status = self.STATUS_RUN
		self.updateBlogData()
		self.updateStatistics()
		self.write("\tThread '" + self.init_tread.getName() + "' is done.")


	def stopBlog(self):
		self.write("Stop " + self.getAccountName() + ".. ")
		if self.init_tread.isAlive():
			self.write("\tWaiting thread '" + self.init_tread.getName() + "' to stop..")
			self.init_tread.join()
		self.status = self.STATUS_STOP
		self.updateBlogData()
		self.stopTimers()
		self.updateStatistics()
		self.write("\t" + self.getAccountName() + " stopped.")


	def randomTag(self):
		new_tags = []
		if self.tags == []:
			return ""
		for tag in self.tags:
			if not tag in self.notGoodTags:
				new_tags.append(tag)
		tag_pos = random.randint(0, len(new_tags)-1)
		return new_tags[tag_pos]


	def randomF4F(self):
		tag_pos = random.randint(0, len(self.f4fs)-1)
		return self.f4fs[tag_pos]


	def randomL4L(self):
		tag_pos = random.randint(0, len(self.l4ls)-1)
		return self.l4ls[tag_pos]


	def setTimers(self):
		if self.timer_post > 0:
			self.set_post_timer()
			self.isPosting = True
		else:
			self.isPosting = False
		if self.timer_follow > 0:
			self.set_follow_timer()
			self.isFollowing = True
		else:
			self.isFollowing = False
		if self.timer_like > 0:
			self.set_like_timer()
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


	def set_post_timer(self):
		timer_post = random.randint((self.timer_post) - (self.TIMERHALFWINDOW*60), (self.timer_post) + (self.TIMERHALFWINDOW*60))
		tp = threading.Timer(timer_post, self.post) # in seconds
		tp.start() 
		self.timers[self.strID + "-post"] = tp
		deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + timer_post)).strftime('%H:%M:%S %d/%m')
		self.timersTime[self.strID + "-post"] = deadline
		self.write("\tcreated new thread for post after " + seconds2timeStr(timer_post))
		self.updateStatistics()


	def set_like_timer(self):
		timer_like = random.randint((self.timer_like) - (self.TIMERHALFWINDOW*60), (self.timer_like) + (self.TIMERHALFWINDOW*60))
		tl = threading.Timer(timer_like, self.like) # in seconds
		tl.start() 
		self.timers[self.strID + "-like"] = tl
		deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + timer_like)).strftime('%H:%M:%S %d/%m')
		self.timersTime[self.strID + "-like"] = deadline
		self.write("\tcreated new thread for like after " + seconds2timeStr(timer_like))
		self.updateStatistics()


	def set_follow_timer(self):
		timer_follow = random.randint((self.timer_follow) - (self.TIMERHALFWINDOW*60), (self.timer_follow) + (self.TIMERHALFWINDOW*60))
		tf = threading.Timer(timer_follow, self.follow) # in seconds
		tf.start() 
		self.timers[self.strID + "-follow"] = tf
		deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + timer_follow)).strftime('%H:%M:%S %d/%m')
		self.timersTime[self.strID + "-follow"] = deadline
		self.write("\tcreated new thread for follow after " + seconds2timeStr(timer_follow))
		self.updateStatistics()


	def checkData(self):
		bn = self.getAccountName()
		if bn != "not available":
			self.write("\tCheck data in DB for " + bn + ":")
			self.checkNeedNewPosts()
			self.checkNeedNewFollows()


	def checkNeedNewPosts(self):
		bn = self.getAccountName()
		# Check num Post
		posts = self.dbManager.countPost(bn)
		self.write("\t   check #post.. needed " + str(self.num_post_xt) + ".. ")
		if posts >= self.num_post_xt:
			self.write("\t\tfound " + str(posts) + ", ok")
		else:
			self.write("\t\tfound " + str(posts) + ", needed at least " + str(self.num_post_xt) + "")
			self.search_post(num_post=(self.num_post_xt-posts))  


	def post(self, num_posts = -1, isDump = False):
		blogname = self.getAccountName()
		if not self.isTest:
			self.set_post_timer()
		self.write("Posting " + blogname + ":")
		if num_posts == -1:
			num_posts = self.num_post_xt
		posts = self.dbManager.getPosts(blogname,num_posts)
		if isDump:
			self.write(str(posts)) 
		counter = 0
		for post in posts:
			try:
				if isDump:
					self.write(str(post)) 
				self.postSocial(post)
				args = (post['id'],blogname)
				self.dbManager.delete("PostsLikes",args)
				counter += 1
				self.write("\tposted " + str(counter) + "/" + str(num_posts))
			except Exception,msg:
				self.writeError("\tError: exception on " + blogname + " reblogging\n" + str(msg))
		self.write("\tposted " + str(counter) + " posts!")
		if not self.isTest:
			self.checkNeedNewPosts()
		self.updateBlogData()


	def follow(self, num_follows = -1, isDump = False):
		blogname = self.getAccountName()
		if not self.isTest:
			self.set_follow_timer()
		self.write("Following " + blogname + ":")
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
		self.write("Unfollowing " + blogname + ":")
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
					self.write("\tUnfollowed " + str(counterUnfollow) + "/" + str(self.num_follow_xt))
				else:
					# else re-append at the end
					self.followingList.append(blog_name_unfollow)
			except IndexError, msg:
				self.writeError("\tError: " + str(msg))
			except Exception, msg:
				self.writeError("\tError: exception on " + blogname + " unfollow!")
		self.write("\tUnfollowed " + str(counterUnfollow) + " blogs.")


	def canUnfollow(self,blog2unfollow):
		return True


	def like(self, num_likes = -1, isDump = False):
		blogname = self.getAccountName()
		if not self.isTest:
			self.set_like_timer()
		self.write("Liking " + blogname + ":")
		if num_likes == -1:
			num_likes = self.num_like_xt
		self.likeSocial(num_likes, isDump)
		self.updateBlogData()


	def checkFollowingStatus(self):
		blogname = self.getAccountName()
		if time.time() >= self.updateFollowersTime:
			self.write("Time to update follower and following status..")
			# Get Followers
			self.getFollowers()
			# Update following status in db
			self.write("\tUpdate Following status.. ")
			self.dbManager.setAllFollowingUnfollowed(blogname)
			for follower in self.followersList:
				if follower in self.followingList:
					self.dbManager.setFollowingFollowed(blogname, follower, True)
			self.updateMatchesStatistics()
			self.followingList = self.dbManager.getFollowing(blogname)
			# Unfollow who did not follow me back after a while
			self.write("\tUnfollow who did not follow me back after a while.. ")
			timeLimit = int((time.time() - self.FOLLOWING_TRASH_TIME) * self.TIME_FACTOR)
			toUnfollow = self.dbManager.getFollowingTrash(blogname, timeLimit)
			self.write(str(len(toUnfollow)) + " to unfollow.. ")
			counterUnfollowed = 0
			for toUnfollowName in toUnfollow:
				try:
					self.unfollowSocial(toUnfollowName)
					self.followingList.remove(toUnfollowName)
					args = (blogname, toUnfollowName)
					self.dbManager.delete("Following",args)
					counterUnfollowed += 1
				except Exception, msg:
					self.writeError("\tError: exception on " + blogname + " unfollow for time!")
			self.write("unfollowed " + str(counterUnfollowed) + ".\n")
		# Check if too many follow and unfollow in that case
		if len(self.followingList) >= self.LIMITFOLLOW:
			self.write("\t#Following: " + str(len(self.followingList)) + " >= max # following (" + str(self.LIMITFOLLOW) + ") -> need to unfollow!")
			self.unfollow()
		else:
			self.write("\t#Following: " + str(len(self.followingList)) + " < max # following (" + str(self.LIMITFOLLOW) + ") -> NO need to unfollow!")
			


	def initFollowings(self):
		self.write("\tInitialize Following.. ")
		self.followingList = []
		blogname = self.getAccountName()
		current_num_followings = self.dbManager.countFollowing(blogname)
		if current_num_followings != self.data['following']:
			following = self.getFollowing()
		else:
			self.write("\t\tGet Following List from DB.. ")
			following = self.dbManager.getFollowing(blogname)
			self.write("\t\tok")
		args = (blogname,)
		self.dbManager.deleteAll("Following",args)
		self.checkFollowingFollowed(following)
		self.write("\tDone.")


	def initFollowers(self):
		self.write("\tInitialize Followers.. ")
		self.followersList = []
		self.getFollowers()
		self.orderedFollowersList = sorted(self.followersList)
		self.write("\tDone.")


	def getFollowers(self):
		self.write("\t\tGet Followers List.. ")
		self.followersList = self.getFollowersSocial()
		self.updateFollowersTime = time.time() + self.FOLLOWERS_UPDATE_TIME


	def getFollowing(self):
		self.write("\t\tGet Following List.. ")
		return self.getFollowingsSocial()


	def checkFollowingFollowed(self, following): 
		blogname = self.getAccountName()
		counter = 0
		count_final_str = str(len(following))
		following2insert = []
		while following != []:
			follow = following.pop()
			counter += 1
			self.write("\t\tCheck following " + str(counter) + "/" + count_final_str)
			if binarySearch(follow, self.orderedFollowersList):
				args = (blogname, follow, True, int(time.time() * self.TIME_FACTOR))
			else:
				args = (blogname, follow, False, int(time.time() * self.TIME_FACTOR))
			following2insert.append(args)
		self.write("\t\tInsert following in DB.. ")
		self.dbManager.addList("Following", following2insert)
		self.write("\t\tok!")
		self.followingList = self.dbManager.getFollowing(blogname)


	def clearDB(self):
		blogname = self.getAccountName()
		self.write("Clear DB tables for " + blogname + ".. ")
		self.dbManager.clearDB(blogname)
		self.write("done.")




