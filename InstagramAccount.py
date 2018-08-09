import os
import sys
import csv
import time
import pickle
import random
from datetime import date

import Account
import Utils
import Sender


class InstagramAccount(Account.Account):

	LIMITFOLLOW = 7000

	percF4F = 1/2
	percNotF4F = 1/2

	MAX_RETRIEVED_MEDIA = 10
	MAX_RETRIEVED_LIKE = 10
	MAX_RETRIEVED_COMMENTS = 10

	FSTATS_TRASH_TIME = 60*60*24*20		# 20 days

	MIN_TIME_BETWEEN_ACTIONS = 30		# seconds
	MAX_TIME_BETWEEN_ACTIONS = 40		# seconds 

	DUMP_DIRECTORY = "dump"


	def __init__(self, accounts, account, tags, blogs):
		super(InstagramAccount, self).__init__(accounts, account['ID'], account['Mail'], account['Type'],account['Username'])
		self.username = account['Username']
		self.password = account['Password']
		self.accountName = account['Name']
		self.tags = Utils.tags2list(tags)
		self.blogs = Utils.blogs2list(blogs)
		self.data = self.initData()
		self.num_post_xd = int(account['PostXD'])
		self.num_follow_xd = int(account['FollowXD'])
		self.num_like_xd = int(account['LikeXD'])
		self.num_post_xt = int(account['PostXT'])
		self.num_follow_xt = int(account['FollowXT'])
		self.num_like_xt = int(account['LikeXT'])
		self.status = self.STATUS_STOP
		self.loadStatistics()
		self.initDailyStats()


	def post_insta_request(self, params, firstTime=False):
		return Sender.post_insta_request(self, params)


	def getAccountName(self):
		return self.username


	def getSocialName(self):
		return "instagram"


	def initData(self):
		return {'private': "not available",
				'following': "not available",
				'followers': "not available",
				'messages': "not available",
				'name': "not available",
				'posts': "not available",
				'usertags': "not available"
				}


	def initStatistics(self):
		self.statistics = { 'timer_follow_match': {	'P_f+rl': 1, 'P_f': 1, 'R_f+rl': 1, 'R_f': 1 },
							'timer_follow_tot':   { 'P_f+rl': 1, 'P_f': 1, 'R_f+rl': 1, 'R_f': 1 },
							'timer_follow_succ':  {	'P_f+rl': 1.0, 'P_f': 1.0, 'R_f+rl': 1.0, 'R_f': 1.0 },
							'timer_follow_prob':  {	'P_f+rl': 1.0/4, 'P_f': 1.0/4, 'R_f+rl': 1.0/4, 'R_f': 1.0/4 },
							'timer_like_match':   { 'R_l+f+rl': 1, 'R_l+f': 1, 'R_l+rl': 1, 'R_l': 1, 'rl': 1 },
							'timer_like_tot': 	  { 'R_l+f+rl': 1, 'R_l+f': 1, 'R_l+rl': 1, 'R_l': 1, 'rl': 1 },
							'timer_like_succ': 	  { 'R_l+f+rl': 1.0, 'R_l+f': 1.0, 'R_l+rl': 1.0, 'R_l': 1.0, 'rl': 1.0 },
							'timer_like_prob': 	  { 'R_l+f+rl': 1.0/5, 'R_l+f': 1.0/5, 'R_l+rl': 1.0/5, 'R_l': 1.0/5, 'rl': 1.0/5 }
							}
		self.dumpStatistics()


	def dumpStatistics(self):
		pickle.dump(self.statistics,open(self.DUMP_DIRECTORY + "/" + self.username + ".p","wb"))


	def loadStatistics(self):
		if os.path.exists(self.DUMP_DIRECTORY):
			if os.path.exists(self.DUMP_DIRECTORY + "/" + self.username + ".p"):
				try:
					self.statistics = pickle.load(open(self.DUMP_DIRECTORY + "/" + self.username + ".p","rb"))
				except Exception, msg:
					self.output.writeErrorLog("Error: " + str(msg))
			else:
				self.initStatistics()
		else:
			os.mkdir(self.DUMP_DIRECTORY)
			self.initStatistics()


	def initDailyStats(self):
		self.output.writeLog("Initialize daily statistics.. ")
		if not os.path.exists(self.DUMP_DIRECTORY + "/daily_" + self.username + ".csv"):
			self.output.writeLog("dump file not found, creating new one.. ")
			with open(self.DUMP_DIRECTORY + "/daily_" + self.username + ".csv", 'w') as f:
				writer = csv.writer(f)
				writer.writerow(["date", "posts", "likes", "follows", "unfollows", "followers", "followings"]) 
			self.output.writeLog("ok")
		else:
			self.output.writeLog("file already exists, ok")


	def dumpDailyStats(self):
		now = date.today()
		if self.today < now:
			with open(self.DUMP_DIRECTORY + "/daily_" + self.username + ".csv", 'a') as f:
				writer = csv.writer(f)
				writer.writerow([self.today, self.todayPosts, self.todayLikes, self.todayFollows, self.todayUnfollows, self.data['followers'], self.data['following']]) 
			self.today = now
			self.todayPosts = 0
			self.todayLikes = 0
			self.todayFollows = 0
			self.todayUnfollows = 0

	def updateMatchStatistics(self, group, action):
		self.statistics[group + "_match"][action] += 1
		self.updateSuccProbStatistics(group, action)


	def updateMatchesStatistics(self):
		bn = self.getAccountName()
		for follow in self.followersList:
			fstats = self.dbManager.getFstats(bn,follow)
			if fstats != []:
				for fstat in fstats:
					if fstat['action'][2] == 'f':
						self.updateMatchStatistics('timer_follow', fstat['action'])
					else:
						self.updateMatchStatistics('timer_like', fstat['action'])
					updateMatchTagsBlogsStats(fstat['gotBy'])
				args = (bn,follow)
				self.dbManager.delete('Fstats',args)
		# Delete old ones:
		timeLimit = int((time.time() - self.FSTATS_TRASH_TIME) * self.TIME_FACTOR)
		self.dbManager.deleteFstatsTrash(bn,timeLimit)


	def updateTotStatistics(self, group, action):
		self.statistics[group + "_tot"][action] += 1
		self.updateSuccProbStatistics(group, action)


	def updateSuccProbStatistics(self, group, action):
		match = float(self.statistics[group + "_match"][action])
		tot = float(self.statistics[group + "_tot"][action])
		self.statistics[group + "_succ"][action] = match / tot
		sum_succ = 0
		for key, item in self.statistics[group + "_succ"].iteritems():
			sum_succ += item
		for key in self.statistics[group + "_prob"]:
			self.statistics[group + "_prob"][key] = self.statistics[group + "_succ"][key] / sum_succ
		self.dumpStatistics()


	def addStatistics(self, followedBlog, action, gotBy):
		self.output.writeLog("Add satistics: blog=" + followedBlog + " action=" + action + " gotBy=" + gotBy)
		if (action == 'rl') or (action[2] == 'l'):
			group = 'timer_like'
		else:
			group = 'timer_follow'
		self.updateTotStatistics(group, action)
		self.updateTotTagsBlogsStats(gotBy)
		args = (self.getAccountName(), followedBlog, action, gotBy, int(time.time() * self.TIME_FACTOR))
		self.dbManager.add("Fstats",args)


	def updateTotTagsBlogsStats(self, gotBy):
		if len(gotBy) > 0:
			if gotBy[0] == 'b':
				blog = gotBy[2:]
				self.blogs[blog]['Used'] += 1 
			elif gotBy[0] == 't':
				tag = gotBy[2:]
				self.tags[tag]['Used'] += 1
			else:
				pass


	def updateMatchTagsBlogsStats(self, gotBy):
		if len(gotBy) > 0:
			if gotBy[0] == 'b':
				blog = gotBy[2:]
				self.blogs[blog]['Success'] += 1 
			elif gotBy[0] == 't':
				tag = gotBy[2:]
				self.tags[tag]['Success'] += 1
			else:
				pass


	def checkResponse(self, res):
		"Check if there is an error in response"
		if res != None:
			return True
		else:
			return False


	def updateAccount(self, firstTime=False):
		if firstTime:
			self.output.write("\tUpdate " + self.getAccountName() + ".. ")
		else:
			self.output.writeLog("\tUpdate " + self.getAccountName() + ".. ")
		try:
			ibi = self.post_insta_request({'action': 'get_insta_blog_info'}, firstTime)
			if self.checkResponse(ibi):
				self.data['private'] = ibi['private']
				self.data['following'] = ibi['following']
				self.data['followers'] = ibi['follower']
				self.data['messages'] = ibi['message']
				self.data['name'] = ibi['name']
				self.data['posts'] = ibi['post']
				self.data['usertags'] = ibi['usertags']
				self.accounts.matches[ibi['name']] = self.strID
				if firstTime:
					print "ok."
				else:
					self.output.writeLog("ok.")
			else:
				if firstTime:
					print "Error: cannot update."
				else:
					self.output.writeErrorLog("Error: cannot update.")
		except Exception, msg:
			if firstTime:
				print "Error Exception:\n" + str(msg)
			else:
				self.output.writeErrorLog("Error Exception:\n" + str(msg))
						

	def updateAccountData(self, firstTime=False):
		if firstTime:
			self.output.write("\tUpdate " + self.getAccountName() + ".. ")
		else:
			self.output.writeLog("\tUpdate " + self.getAccountName() + ".. ")
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
		if (self.strID + "-post") in self.timersTime:
			post_data_up["Deadline_Post"] = self.timersTime[self.strID + "-post"]
		if (self.strID + "-follow") in self.timersTime:
			post_data_up["Deadline_Follow"] = self.timersTime[self.strID + "-follow"]
		if (self.strID + "-like") in self.timersTime:
			post_data_up["Deadline_Like"] = self.timersTime[self.strID + "-like"]
		up_res = self.post_request(post_data_up)
		if up_res != None:
			# update tags statistics
			if firstTime:
				self.output.write("update tags stats.. ")
			else:
				self.output.writeLog("update tags stats.. ")
			for tag in self.tags:
				self.post_request({"action": "update_tags_stats", "ID": self.account_id, "Tag": tag, "Success": self.tags[tag]['Success'], "Used": self.tags[tag]['Used']})
			# update status
			if firstTime:
				self.output.write("update status.. ")
			else:
				self.output.writeLog("update status.. ")
			self.updateStatus()
			if firstTime:
				print "end of update."
			else:
				self.output.writeLog("end of update.")				


	def updateUpOp(self, newAccount):
		if self.username != newAccount['Username']:
			self.output.writeLog("\t\t    Username: " + self.username + " -> " + newAccount['Username'])
			self.username = newAccount['Username']
		if self.password != newAccount['Password']:
			self.output.writeLog("\t\t    Password: " + self.password + " -> " + newAccount['Password'])
			self.password = newAccount['Password']
		super(InstagramAccount, self).updateUpOp(newAccount)


	def copyBlog(self, blog_to_copy, limitMax, counter):
		self.output.writeLog("Method 'copyBlog' not implemented for Instagram account!")


	def waitInsta(self, little=False):
		if little:
			secs = random.randint(1, 4)
		else:
			secs = random.randint(self.MIN_TIME_BETWEEN_ACTIONS, self.MAX_TIME_BETWEEN_ACTIONS)
		self.output.writeLog("Wait " + str(secs) + "seconds")
		time.sleep(secs)
		self.output.writeLog("End wait.")


	def calc_time_post_follow(self):
		f_tf, l_tf = self.calc_expected_FL_TF()
		f_tl, l_tl = self.calc_expected_FL_TL()

		nl = ((self.num_like_xd * f_tf) - (self.num_follow_xd * l_tf)) / float(self.num_like_xt * ((l_tl * f_tf) - (f_tl * l_tf)))
		nf = ((self.num_follow_xd * l_tl) - (self.num_like_xd * f_tl)) / float(self.num_follow_xt * ((l_tl * f_tf) - (f_tl * l_tf)))

		self.output.writeLog("\tCalcule timers for " + self.getAccountName() + ":")
		if self.num_post_xd == 0:
			self.timer_post = 0
			self.output.writeLog("\t\tnever post")
		else:
			self.timer_post = int((24*60*60/(self.num_post_xd/self.num_post_xt))+0.5)
			self.output.writeLog("\t\tpost every " + Utils.seconds2timeStr(self.timer_post))	
		self.timer_follow = int((24*60*60/nf)+0.5)
		self.output.writeLog("\t\tfollow every " + Utils.seconds2timeStr(self.timer_follow))
		self.timer_like = int((24*60*60/nl)+0.5)
		self.output.writeLog("\t\tlike every " + Utils.seconds2timeStr(self.timer_like))


	def calc_expected_FL_TF(self):
		""" returns a tuple of 2 where:
			1. the prob that a follow occurs when timer follow triggers
			2. the prob that a like occurs when timer follow triggers """
		return 1, self.statistics['timer_follow_prob']['P_f+rl'] + self.statistics['timer_follow_prob']['R_f+rl']


	def calc_expected_FL_TL(self):
		""" returns a tuple of 2 where:
			1. the prob that a follow occurs when timer like triggers
			2. the prob that a like occurs when timer like triggers """
		tlp = self.statistics['timer_like_prob']
		expected_f = tlp['R_l+f+rl'] + tlp['R_l+f']
		expected_l = (2 * tlp['R_l+f+rl']) + tlp['R_l+f'] + (2 * tlp['R_l+rl']) + tlp['R_l'] + tlp['rl'] 
		return expected_f, expected_l


	def search_post(num_post):
		pass


	def checkNeedNewFollows(self):
		bn = self.getAccountName()
		# Check num Follows
		follows = self.dbManager.countFollow(bn)
		self.output.writeLog("\t   check #follow.. ")
		if follows >= self.num_follow_xt:
			self.output.writeLog("found " + str(follows) + ", ok")
		else:
			self.output.writeLog("found " + str(follows) + ", needed at least " + str(self.num_follow_xt))
			self.searchNewFollows(self.num_follow_xt-follows)


	def searchNewFollows(self, num_follows):
		# count how many follow take for every blog
		num_following_blogs = len(self.blogs)
		if num_following_blogs >= num_follows:
			followXblog = 1
		elif num_following_blogs > 0:
			followXblog = int(num_follows/num_following_blogs)+1
		else:
			followXblog = 0
		self.output.writeLog("\t      Getting follows..")
		for blog in self.blogs:
			# take some new followers from that blog
			counter = 0
			blog_id = self.getIdByUsernameInsta(blog)
			if blog_id == None:
				self.output.writeErrorLog("\t         Error (None response) for '" + blog + "' -> skip!")
				continue
			followers = self.getFollowersSocial(user=blog_id, maxNum=followXblog)
			if followers == None:
				self.output.writeErrorLog("\t         Error (None response getFollowersSocial) for '" + blog + "'")
			else:
				for follow in followers:
					if (not follow in self.followersList) and (not follow in self.followingList):
						self.addFollowToDB(follow)
						counter += 1
						self.output.writeLog("\t         from " + blog + ".. " + str(counter))
			self.waitInsta(little=True)
		if len(self.tags) > 0:
			tag = self.selectTag()
			if self.MAX_RETRIEVED_COMMENTS + self.MAX_RETRIEVED_LIKE >= num_follows:
				popularPosts = 1
			else:
				popularPosts = int(num_follows/(self.MAX_RETRIEVED_COMMENTS + self.MAX_RETRIEVED_LIKE))+1
			counterMedia = 0
			counterLikers = 0
			counterComments = 0
			media = self.getTaggedPopularInsta(tag, popularPosts)
			if media == None:
				self.output.writeErrorLog("\t         error on getTaggedPopularInsta")
			else:
				for post in media:
					if (not post['userID'] in self.followingList) and (not post['userID'] in self.followersList):
						self.addFollowToDB(post['userID'])
						counterMedia += 1
						self.output.writeLog("\t         from posts: " + str(counterMedia) + ", from likes: " + str(counterLikers) + ", from comments: " + str(counterComments))
					self.waitInsta(little=True)
					likers = self.getMediaLikersInsta(post['mediaID'], self.MAX_RETRIEVED_LIKE)
					if likers == None:
						self.output.writeErrorLog("\t         Error: None response for getMediaLikersInsta")
					else:
						for liker in likers: 
							if (not liker in self.followingList) and (not liker in self.followersList):
								self.addFollowToDB(liker)
								counterLikers += 1
								self.output.writeLog("\t         from posts: " + str(counterMedia) + ", from likes: " + str(counterLikers) + ", from comments: " + str(counterComments))
					self.waitInsta(little=True)
					comments = self.getMediaCommentsInsta(post['mediaID'], self.MAX_RETRIEVED_COMMENTS)
					if comments == None:
						self.output.writeErrorLog("\t         Error: None response for getMediaCommentsInsta")
					else:
						for comment in comments: 
							if (not comment in self.followingList) and (not comment in self.followersList):
								self.addFollowToDB(comment)
								counterComments += 1
								self.output.writeLog("\t         from posts: " + str(counterMedia) + ", from likes: " + str(counterLikers) + ", from comments: " + str(counterComments))
					self.waitInsta(little=True)
		else:
			self.output.writeLog("\t         No Tags inserted.. cannot get new follows!")


	def postSocial(self, post):
		self.output.writeLog("Method 'post' not implemented for Instagram account!")


	def followSocial(self, num_follows, isDump):
		blogname = self.getAccountName()
		alreadyFollowed = []
		num_f_P = 0
		num_frl_P = 0
		num_f_R = 0
		num_frl_R = 0
		errors = 0
		for counter in range(0,num_follows):
			follow_method = Utils.selectWithProb(self.statistics['timer_follow_prob'].keys(),self.statistics['timer_follow_prob'].values())
			if follow_method[0] == 'P':
				could_get, follow = self.getNewFollowFromDB(alreadyFollowed)
				if not could_get:
					errors += 1
					self.prettyLogFollow(counter, num_follows, follow_method, num_f_P, num_frl_P, num_f_R, num_frl_R, errors, could_get=False)
					continue
				alreadyFollowed.append(follow)
				if follow_method == "P_f+rl":
					self.output.writeLog("Follow Method for " + str(counter + 1) + ": " + follow_method)
					self.followAndRandomLike(follow, follow_method, "", isDump)
					num_frl_P += 1
				else:
					self.output.writeLog("Follow Method for " + str(counter + 1) + ": " + follow_method)
					self.justFollow(follow, follow_method, "", isDump)
					num_f_P += 1
			else:
				could_get, follow, tag = self.getNewFollowFromSearch(alreadyFollowed)
				if not could_get:
					errors += 1
					self.prettyLogFollow(counter, num_follows, follow_method, num_f_P, num_frl_P, num_f_R, num_frl_R, errors, could_get=False)
					continue
				alreadyFollowed.append(follow)
				gotBy = "t_" + tag
				if follow_method == "R_f+rl":
					self.output.writeLog("Follow Method for " + str(counter + 1) + ": " + follow_method)
					self.followAndRandomLike(follow, follow_method, gotBy, isDump)
					num_frl_R += 1
				else:
					self.output.writeLog("Follow Method for " + str(counter + 1) + ": " + follow_method)
					self.justFollow(follow, follow_method, gotBy, isDump)
					num_f_R += 1
			self.prettyLogFollow(counter, num_follows, follow_method, num_f_P, num_frl_P, num_f_R, num_frl_R, errors, could_get=True)


	def prettyLogFollow(self, counter, num_follows, follow_method, num_f_P, num_frl_P, num_f_R, num_frl_R, errors, could_get=True):
		toLog = "\tFollow " + str(counter + 1) + " of " + str(num_follows) + " (FM: " + follow_method + ", CG: " + str(could_get) + "):"
		toLog += str(num_f_P) + " f_P, " + str(num_frl_P) + " f+rl_P, " + str(num_f_R) + " f_R, " + str(num_frl_R) + " frl_R"
		toLog += " ( " + str(errors) + " errors )"
		self.output.writeLog(toLog)


	def getNewFollowFromDB(self, alreadyFollowed):
		blogname = self.getAccountName()
		while True:
			follow = self.dbManager.getFollows(blogname,1)
			if follow == []:
				self.output.writeErrorLog("Error: no follow in DB!")
				return False, None
			if follow[0] == None:
				self.output.writeErrorLog("Error: follow[0] = None!")
				self.output.writeErrorLog(str(follow))
				return False, None
			if not follow[0] in alreadyFollowed:
				return True, follow[0]
			else:
				self.deleteFollowFromDB(follow[0])


	def deleteFollowFromDB(self, follow):
		blogname = self.getAccountName()
		args = (follow,blogname)
		self.dbManager.delete("Follow",args)


	def addFollowToDB(self, follow):
		blogname = self.getAccountName()
		args = (follow,blogname,int(time.time()))
		self.dbManager.add("Follow",args)


	def getNewFollowFromSearch(self, alreadyFollowed):
		max_errors = 10
		num_errors = 0
		blogname = self.getAccountName()
		while True:
			tag = self.selectTag()
			follow = self.getTaggedRecentInsta(tag, 1)
			if follow == None:
				self.output.writeErrorLog("Error: 'None' response for find recent media tagged '" + tag + "'")
				num_errors += 1
				if num_errors >= max_errors:
					self.output.writeErrorLog("Error: max num errors reached for getNewFollowFromSearch!")
					return False, None
				else:
					self.waitInsta(little=True)
			elif follow == []:
				self.output.writeErrorLog("Error: cannot find recent media tagged '" + tag + "'")
				return False, None
			elif not follow[0]['userID'] in alreadyFollowed:
				return True, follow[0]['userID'], tag
			else:
				num_errors += 1
				if num_errors >= max_errors:
					self.output.writeErrorLog("Error: max num errors reached for getNewFollowFromSearch!")
					return False, None
				else:
					self.waitInsta(little=True)


	def followAndRandomLike(self, follow, follow_method, gotBy, isDump):
		if isDump:
			self.output.writeLog("follow and random like: " + str(follow))
		self.followInsta(follow)
		self.randomMediaLikeInsta(follow)
		self.deleteFollowFromDB(follow)
		self.addStatistics(follow, follow_method, gotBy)


	def justFollow(self, follow, follow_method, gotBy, isDump):
		if isDump:
			self.output.writeLog("just follow: " + str(follow))
		self.followInsta(follow)
		self.deleteFollowFromDB(follow)
		self.addStatistics(follow, follow_method, gotBy)


	def followInsta(self, blog2follow):
		self.output.writeLog("Following '" + str(blog2follow) + "'")
		self.post_insta_request({'action': 'follow_insta', 'user': str(blog2follow)})
		self.output.writeLog("Followed.")
		self.followingList.append(blog2follow)
		self.todayFollows += 1
		self.waitInsta()


	def unfollowSocial(self, blog2unfollow):
		self.output.writeLog("Unfollowing '" + str(blog2unfollow) + "'")
		self.post_insta_request({'action': 'unfollow_insta', 'user': str(blog2unfollow)})
		self.output.writeLog("Unfollowed.")
		self.todayUnfollows += 1
		self.waitInsta()


	def likeSocial(self, num_likes, isDump):
		blogname = self.getAccountName()
		num_lfrl_R = 0
		num_lf_R = 0
		num_lrl_R = 0
		num_l_R = 0
		num_rl = 0
		errors = 0
		for counter in range(0,num_likes):
			like_method = Utils.selectWithProb(self.statistics['timer_like_prob'].keys(),self.statistics['timer_like_prob'].values())
			if like_method[0] == 'R':
				tag = self.selectTag()
				gotBy = "t_" + tag
				self.output.writeLog("\tGet recent media with tag '" + tag + "'.. ")
				media = self.getTaggedRecentInsta(tag,1)
				if media == None:
					errors += 1
					self.prettyLogLike(counter, num_likes, like_method, num_l_R, num_lf_R, num_lrl_R, num_lfrl_R, num_rl, errors)
					continue
				elif media == []:
					self.output.writeLog("no recent tag for '" + tag + "'!")
					errors += 1
					self.prettyLogLike(counter, num_likes, like_method, num_l_R, num_lf_R, num_lrl_R, num_lfrl_R, num_rl, errors)
					continue
				else:
					self.output.writeLog("ok")
				media = media[0]
				if like_method == 'R_l':
					self.output.writeLog("Like Method for " + str(counter + 1) + ": " + like_method)
					self.justLike(media, like_method, gotBy, isDump)
					num_l_R += 1
				elif like_method == 'R_l+f':
					self.output.writeLog("Like Method for " + str(counter + 1) + ": " + like_method)
					self.likeAndFollow(media, like_method, gotBy, isDump)
					num_lf_R += 1
				elif like_method == 'R_l+rl':
					self.output.writeLog("Like Method for " + str(counter + 1) + ": " + like_method)
					self.likeAndRandomLike(media, like_method, gotBy, isDump)
					num_lrl_R += 1
				elif like_method == 'R_l+f+rl':
					self.output.writeLog("Like Method for " + str(counter + 1) + ": " + like_method)
					self.likeFollowAndRandomLike(media, like_method, gotBy, isDump)
					num_lfrl_R += 1
			else:
				could_get, user = self.getNewFollowFromDB([])
				if not could_get:
					self.output.writeLog("no follow in DB!")
					errors += 1
					self.prettyLogLike(counter, num_likes, like_method, num_l_R, num_lf_R, num_lrl_R, num_lfrl_R, num_rl, errors, could_get)
					continue
				self.output.writeLog("Like Method for " + str(counter + 1) + ": " + like_method)
				self.randomLike(user, like_method, "", isDump)
				num_rl += 1
			self.prettyLogLike(counter, num_likes, like_method, num_l_R, num_lf_R, num_lrl_R, num_lfrl_R, num_rl, errors, could_get=None)


	def prettyLogLike(self, counter, num_likes, like_method, num_l_R, num_lf_R, num_lrl_R, num_lfrl_R, num_rl, errors, could_get=None):
		toLog = "\tLike " + str(counter + 1) + " of " + str(num_likes) + " (LM: " + like_method 
		if could_get is not None:
			toLog += ", CG: " + could_get
		toLog += "): " + str(num_l_R) + " l_R, " + str(num_lf_R) + " l+f_R, " + str(num_lrl_R) + " l+rl_R, "
		toLog += str(num_lfrl_R) + " l+f+rl_R, " + str(num_rl) + " rl ( " + str(errors) + " errors )"
		self.output.writeLog(toLog)

	
	def justLike(self, media, like_method, gotBy, isDump):
		self.likeInsta(media['mediaID'])
		self.addStatistics(media['userID'], like_method, gotBy)
		if isDump:
			self.output.writeLog(like_method)


	def likeAndFollow(self, media, like_method, gotBy, isDump):
		self.likeInsta(media['mediaID'])
		self.followInsta(media['userID'])
		self.addStatistics(media['userID'], like_method, gotBy)
		if isDump:
			self.output.writeLog(like_method)


	def likeAndRandomLike(self, media, like_method, gotBy, isDump):
		self.likeInsta(media['mediaID'])
		self.randomMediaLikeInsta(media['userID'])
		self.addStatistics(media['userID'], like_method, gotBy)
		if isDump:
			self.output.writeLog(like_method)


	def likeFollowAndRandomLike(self, media, like_method, gotBy, isDump):
		self.likeInsta(media['mediaID'])
		self.followInsta(media['userID'])
		self.randomMediaLikeInsta(media['userID'])
		self.addStatistics(media['userID'], like_method, gotBy)
		if isDump:
			self.output.writeLog(like_method)
		

	def randomLike(self, userID, like_method, gotBy, isDump):
		self.randomMediaLikeInsta(userID)
		self.deleteFollowFromDB(userID)
		self.addStatistics(userID, like_method, gotBy)
		if isDump:
			self.output.writeLog(like_method)


	def likeInsta(self, postID):
		self.output.writeLog("Liking '" + str(postID) + "'")
		response = self.post_insta_request({'action': 'like_insta', 'postID': str(postID)})
		self.output.writeLog("Liked.")
		self.todayLikes += 1
		self.waitInsta()
		return (response is None)


	def getFollowersSocial(self, user=None, maxNum=None):
		""" must return dict with users (dict with name for each user) and total_users (total number of Followers of the blog) """
		params = {'action': 'get_followers_insta'}
		if user != None:
			params['userID'] = str(user)
		if maxNum != None:
			params['maxNum'] = maxNum
		followers = self.post_insta_request(params)
		if user == None:
			if followers == None:
				self.output.writeErrorLog("\t\tGet Followers List.. Error: None response.")
			else:
				self.output.writeLog("\t\tGet Followers List.. " + str(len(followers)) + "/" + str(self.data['followers']))
		return followers


	def getFollowingsSocial(self, user=None):
		""" must return a list with ID for each user """
		if user == None:
			following = self.post_insta_request({'action': 'get_followings_insta'})
		else:
			following = self.post_insta_request({'action': 'get_followings_insta', 'userID': str(user)})
		if following != None:
			self.output.writeLog("\t\tGet Following List.. " + str(len(following)) + "/" + str(self.data['following']))
		else:
			self.output.writeLog("\t\tError: None following\n" + str(following))
		return following


	def getTaggedPopularInsta(self, tag, maxNum):
		return self.post_insta_request({'action': 'getHashtagFeed_insta', 'tag': tag, 'isPopular': True, 'maxNum': maxNum})


	def getTaggedRecentInsta(self, tag, maxNum):
		return self.post_insta_request({'action': 'getHashtagFeed_insta', 'tag': tag, 'isPopular': False, 'maxNum': maxNum})


	def getMediaLikersInsta(self, postID, maxNum):
		return self.post_insta_request({'action': 'get_likers_insta', 'postID': str(postID), 'maxNum': maxNum})


	def getMediaCommentsInsta(self, postID, maxNum):
		return self.post_insta_request({'action': 'get_comments_insta', 'postID': str(postID), 'maxNum': maxNum})


	def getMediaInsta(self, user, maxNum):
		return self.post_insta_request({'action': 'get_insta_media', 'user': str(user), 'maxNum': maxNum})


	def randomMediaLikeInsta(self, user, howMany=1):
		media = self.getMediaInsta(user, self.MAX_RETRIEVED_MEDIA)
		self.output.writeLog("RandomMedias for '" + str(user) + "': " + str(media))
		if media == None:
			self.output.writeErrorLog("\tError: randomMediaLikeInsta media=None for user '" + str(user) + "'")
		elif media == []:
			self.output.writeErrorLog("\tError: randomMediaLikeInsta media=[] for user '" + str(user) + "'")
		else:
			self.waitInsta(little=True)
			for count in range(0,howMany):
				key = random.randint(0, len(media)-1)
				selectedMedia = media.pop(key)
				self.output.writeLog("SelectedMedia: " + str(selectedMedia))
				self.likeInsta(selectedMedia)


	def getIdByUsernameInsta(self, user):
		resp = self.post_insta_request({'action': 'get_id_by_username', 'user': str(user)})
		if resp == None:
			return None
		else:
			return resp[0] 


	def logAccount(self):
		print "\nLog information for " + self.getAccountName() + ":"
		print "ID: " + str(self.account_id)
		print "strID: " + self.strID
		print "mail: " + self.mail
		print "type: " + str(self.account_type)
		print "username: " + self.username
		print "password: " + self.password
		print "tags:"
		for tag in self.tags:
			print "\t" + tag + ": " + str(self.tags[tag]['Success']) + "/" + str(self.tags[tag]['Used']) 
		print "blogs:"
		for blog in self.blogs:
			print "\t" + blog
		print "private: " + str(self.data['private'])
		print "following: " + str(self.data['following'])
		print "followers: " + str(self.data['followers'])
		print "messages: " + str(self.data['messages'])
		print "name: " + self.data['name']
		print "posts: " + str(self.data['posts'])
		print "usertags: " + str(self.data['usertags'])
		# print "url: " + self.data['url']
		print "num_post_xd: " + str(self.num_post_xd)
		print "num_follow_xd: " + str(self.num_follow_xd)
		print "num_like_xd: " + str(self.num_like_xd)
		print "num_post_xt: " + str(self.num_post_xt)
		print "num_follow_xt: " + str(self.num_follow_xt)
		print "num_like_xt: " + str(self.num_like_xt)
		print "status: " + str(self.status)
		pprint(self.statistics)







