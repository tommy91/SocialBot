import os
import sys
import pickle

from Account import *
from Utils import *
import Sender


class InstagramAccount(Account):

	LIMITFOLLOW = 8000

	percF4F = 1/2
	percNotF4F = 1/2

	MAX_RETRIEVED_MEDIA = 10
	MAX_RETRIEVED_LIKE = 10
	MAX_RETRIEVED_COMMENTS = 10

	FSTATS_TRASH_TIME = 60*60*24*20		# 20 days

	MIN_TIME_BETWEEN_ACTIONS = 30		# seconds
	MAX_TIME_BETWEEN_ACTIONS = 40		# seconds 

	DUMP_DIRECTORY = "dump"

	f4fs = ["follow4follow","follow","followback"] 
	l4ls = ["like4like","likeback"]


	def __init__(self, accounts, account, tags, blogs):
		super(InstagramAccount, self).__init__(accounts, account['ID'], account['Mail'], account['Type'])
		self.username = account['Username']
		self.password = account['Password']
		self.post_insta_request = Sender.post_insta_request
		self.tags = tags2list(tags)
		self.blogs = blogs2list(blogs)
		self.data = self.initData()
		self.num_post_xd = int(account['PostXD'])
		self.num_follow_xd = int(account['FollowXD'])
		self.num_like_xd = int(account['LikeXD'])
		self.num_post_xt = int(account['PostXT'])
		self.num_follow_xt = int(account['FollowXT'])
		self.num_like_xt = int(account['LikeXT'])
		self.status = self.STATUS_STOP
		self.loadStatistics()


	def post_request(self, params):
		return Sender.post_request(self, params)


	def post_insta_request(self, params, firstTime=False):
		return Sender.post_insta_request(self, params)


	def getAccountName(self):
		return self.data['name']


	def getSocialName(self):
		return "instagram"


	def initStatistics(self):
		self.statistics = { 'timer_follow_match': {	'f+rl': 1, 'f': 1, 'f4f': 1, 'f4f+rl': 1 },
							'timer_follow_tot':   { 'f+rl': 1, 'f': 1, 'f4f': 1, 'f4f+rl': 1 },
							'timer_follow_succ':  {	'f+rl': float(1), 'f': float(1), 'f4f': float(1), 'f4f+rl': float(1) },
							'timer_follow_prob':  {	'f+rl': 1/float(4), 'f': 1/float(4), 'f4f': 1/float(4), 'f4f+rl': 1/float(4) },
							'timer_like_match':   { 'l4l': 1, 'l4l+f': 1, 'l4l+rl': 1, 'l4l+f+rl': 1, 'l+f+rl': 1,
													'l+f': 1, 'l+rl': 1, 'l': 1, 'rl': 1 },
							'timer_like_tot': 	  { 'l4l': 1, 'l4l+f': 1, 'l4l+rl': 1, 'l4l+f+rl': 1, 'l+f+rl': 1,
													'l+f': 1, 'l+rl': 1, 'l': 1, 'rl': 1 },
							'timer_like_succ': 	  { 'l4l': float(1), 'l4l+f': float(1), 'l4l+rl': float(1), 'l4l+f+rl': float(1), 
													'l+f+rl': float(1), 'l+f': float(1), 'l+rl': float(1), 'l': float(1), 'rl': float(1) },
							'timer_like_prob': 	  { 'l4l': 1/float(9), 'l4l+f': 1/float(9), 'l4l+rl': 1/float(9), 'l4l+f+rl': 1/float(9), 
													'l+f+rl': 1/float(9), 'l+f': 1/float(9), 'l+rl': 1/float(9), 'l': 1/float(9), 
													'rl': 1/float(9) }
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
					self.writeError("Error: " + str(msg))
			else:
				self.initStatistics()
		else:
			os.mkdir(self.DUMP_DIRECTORY)
			self.initStatistics()


	def updateMatchStatistics(self, group, action):
		self.statistics[group + "_match"][action] += 1
		self.updateSuccProbStatistics(group, action)


	def updateMatchesStatistics(self):
		bn = self.getAccountName()
		for follow in self.followersList:
			fstats = self.dbManager.getFstats(bn,follow)
			if fstats != []:
				for fstat in fstats:
					if fstat['action'][0] == 'f':
						self.updateMatchStatistics('timer_follow', fstat['action'])
					else:
						self.updateMatchStatistics('timer_like', fstat['action'])
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


	def addStatistics(self, followedBlog, action):
		if action[0] == 'f':
			group = 'timer_follow'
		else:
			group = 'timer_like'
		self.updateTotStatistics(group, action)
		args = (self.getAccountName(), followedBlog, action, int(time.time() * self.TIME_FACTOR))
		self.dbManager.add("Fstats",args)


	def initData(self):
		return {'private': "not available",
				'following': "not available",
				'followers': "not available",
				'messages': "not available",
				'name': "not available",
				'posts': "not available",
				'usertags': "not available"
				}


	def checkResponse(self, res):
		"Check if there is an error in response"
		if res != None:
			return True
		else:
			return False


	def updateBlog(self, firstTime=False):
		if self.getAccountName() != "not available":
			if firstTime:
				write("\tUpdate " + self.getAccountName() + ".. ")
			else:
				self.write("\tUpdate " + self.getAccountName() + ".. ")
		else:
			if firstTime:
				write("\tUpdate " + self.mail + ".. ")
			else:
				self.write("\tUpdate " + self.mail + ".. ")
		try:
			ibi = self.post_insta_request({'action': 'get_insta_blog_info'}, firstTime=True)
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
					self.write("ok.")
			else:
				if firstTime:
					print "Error: cannot update."
				else:
					self.writeError("Error: cannot update.")
		except Exception, msg:
			if firstTime:
				print "Error Exception:\n" + str(msg)
			else:
				self.writeError("Error Exception:\n" + str(msg))
						

	def updateBlogData(self):
		self.write("\tUpdate " + self.data['name'] + ".. ")
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
			self.write("update status.. ")
			self.updateStatus()
			self.write("end of update.")


	def updateUpOp(self, newAccount):
		if self.username != newAccount['Username']:
			self.write("\t\t    Username: " + self.username + " -> " + newAccount['Username'])
			self.username = newAccount['Username']
		if self.password != newAccount['Password']:
			self.write("\t\t    Password: " + self.password + " -> " + newAccount['Password'])
			self.password = newAccount['Password']
		super(InstagramAccount, self).updateUpOp(newAccount)


	def copyBlog(self, blog_to_copy, limitMax, counter):
		self.write("Method 'copyBlog' not implemented for Instagram account!")


	def waitInsta(self, little=False):
		if little:
			secs = random.randint(1, 4)
		else:
			secs = random.randint(self.MIN_TIME_BETWEEN_ACTIONS, self.MAX_TIME_BETWEEN_ACTIONS)
		time.sleep(secs)


	def calc_time_post_follow(self):
		f_tf, l_tf = self.calc_expected_FL_TF()
		f_tl, l_tl = self.calc_expected_FL_TL()

		nl = ((self.num_like_xd * f_tf) - (self.num_follow_xd * l_tf)) / float(self.num_like_xt * ((l_tl * f_tf) - (f_tl * l_tf)))
		nf = (self.num_like_xd - (nl * self.num_like_xt * l_tl)) / float(self.num_follow_xt * l_tf)

		self.write("\tCalcule timers for " + self.getAccountName() + ":")
		if self.num_post_xd == 0:
			self.timer_post = 0
			self.write("\t\tnever post")
		else:
			self.timer_post = int((24*60*60/(self.num_post_xd/self.num_post_xt))+0.5)
			self.write("\t\tpost every " + seconds2timeStr(self.timer_post))	
		self.timer_follow = int((24*60*60/nf)+0.5)
		self.write("\t\tfollow every " + seconds2timeStr(self.timer_follow))
		self.timer_like = int((24*60*60/nl)+0.5)
		self.write("\t\tlike every " + seconds2timeStr(self.timer_like))


	def calc_expected_FL_TF(self):
		return 1, (self.statistics['timer_follow_prob']['f+rl'] + self.statistics['timer_follow_prob']['f4f+rl'])


	def calc_expected_FL_TL(self):
		tlp = self.statistics['timer_like_prob']
		expected_f = tlp['l4l+f'] + tlp['l4l+f+rl'] + tlp['l+f+rl'] + tlp['l+f']
		expected_l = tlp['l4l'] + tlp['l4l+f'] + (2 * tlp['l4l+rl']) + (2 * tlp['l4l+f+rl']) 
		expected_l += (2 * tlp['l+f+rl']) + tlp['l+f'] + (2 * tlp['l+rl']) + tlp['l'] + tlp['rl'] 
		return expected_f, expected_l


	def checkNeedNewFollows(self):
		bn = self.getAccountName()
		# Check num Follows
		follows = self.dbManager.countFollow(bn)
		self.write("\t   check #follow.. ")
		if follows >= self.num_follow_xt:
			self.write("found " + str(follows) + ", ok")
		else:
			self.write("found " + str(follows) + ", needed at least " + str(self.num_follow_xt))
			self.searchNewFollows(self.num_follow_xt-follows)


	def searchNewFollows(self, num_follows):
		num_following_blogs = len(self.blogs)
		if num_following_blogs >= num_follows:
			followXblog = 1
		elif num_following_blogs > 0:
			followXblog = int(num_follows/num_following_blogs)+1
		else:
			followXblog = 0
		self.write("\t      Getting follows..")
		for blog in self.blogs:
			counter = 0
			blog_id = self.getIdByUsernameInsta(blog)
			if blog_id == None:
				self.writeError("\t         Error (None response) for '" + blog + "' -> skip!")
				continue
			followers = self.getFollowersSocial(user=blog_id, maxNum=followXblog)
			if followers == None:
				self.writeError("\t         Error (None response getFollowersSocial) for '" + blog + "'")
			else:
				for follow in followers:
					if (not follow in self.followersList) and (not follow in self.followingList):
						self.addFollowToDB(follow)
						counter += 1
						self.write("\t         from " + blog + ".. " + str(counter))
			self.waitInsta(little=True)
		if len(self.tags) > 0:
			tag = self.randomTag()
			if self.MAX_RETRIEVED_COMMENTS + self.MAX_RETRIEVED_LIKE >= num_follows:
				popularPosts = 1
			else:
				popularPosts = int(num_follows/(self.MAX_RETRIEVED_COMMENTS + self.MAX_RETRIEVED_LIKE))+1
			counterMedia = 0
			counterLikers = 0
			counterComments = 0
			media = self.getTaggedPopularInsta(tag, popularPosts)
			if media == None:
				self.writeError("\t         error on getTaggedPopularInsta")
			else:
				for post in media:
					if (not post['userID'] in self.followingList) and (not post['userID'] in self.followersList):
						self.addFollowToDB(post['userID'])
						counterMedia += 1
						self.write("\t         from posts: " + str(counterMedia) + ", from likes: " + str(counterLikers) + ", from comments: " + str(counterComments))
					self.waitInsta(little=True)
					likers = self.getMediaLikersInsta(post['mediaID'], self.MAX_RETRIEVED_LIKE)
					if likers == None:
						self.writeError("\t         Error: None response for getMediaLikersInsta")
					else:
						for liker in likers: 
							if (not liker in self.followingList) and (not liker in self.followersList):
								self.addFollowToDB(liker)
								counterLikers += 1
								self.write("\t         from posts: " + str(counterMedia) + ", from likes: " + str(counterLikers) + ", from comments: " + str(counterComments))
					self.waitInsta(little=True)
					comments = self.getMediaCommentsInsta(post['mediaID'], self.MAX_RETRIEVED_COMMENTS)
					if comments == None:
						self.writeError("\t         Error: None response for getMediaCommentsInsta")
					else:
						for comment in comments: 
							if (not comment in self.followingList) and (not comment in self.followersList):
								self.addFollowToDB(comment)
								counterComments += 1
								self.write("\t         from posts: " + str(counterMedia) + ", from likes: " + str(counterLikers) + ", from comments: " + str(counterComments))
					self.waitInsta(little=True)
		else:
			self.write("\t         No Tags inserted.. cannot get new follows!")


	def postSocial(self, post):
		self.write("Method 'post' not implemented for Instagram account!")


	def followSocial(self, num_follows, isDump):
		blogname = self.getAccountName()
		alreadyFollowed = []
		num_f = 0
		num_f4f = 0
		num_frl = 0
		num_f4frl = 0
		errors = 0
		for counter in range(0,num_follows):
			seed = random.random()
			tfp = self.statistics['timer_follow_prob']
			if seed <= (tfp['f+rl'] + tfp['f']):
				could_get, follow = self.getNewFollowFromDB(alreadyFollowed)
				if not could_get:
					errors += 1
					self.write("\t" + str(counter + 1) + " of " + str(num_follows) + ": " + str(num_f) + " f, " + str(num_frl) + " f+rl, " + str(num_f4f) + " f4f, " + str(num_f4frl) + " f4f+rl" + " ( " + str(errors) + " errors )")
					continue
				alreadyFollowed.append(follow)
				if seed <= tfp['f+rl']:
					self.followAndRandomLike(follow, isDump)
					num_frl += 1
				else:
					self.justFollow(follow, isDump)
					num_f += 1
			else:
				could_get, follow = self.getNewFollowFromSearch(alreadyFollowed)
				if not could_get:
					errors += 1
					self.write("\t" + str(counter + 1) + " of " + str(num_follows) + ": " + str(num_f) + " f, " + str(num_frl) + " f+rl, " + str(num_f4f) + " f4f, " + str(num_f4frl) + " f4f+rl" + " ( " + str(errors) + " errors )")
					continue
				alreadyFollowed.append(follow)
				if seed <= (tfp['f+rl'] + tfp['f'] + tfp['f4f']):
					self.justFollow(follow, isDump, isF4F = True)
					num_f4f += 1
				else:
					self.followAndRandomLike(follow, isDump, isF4F = True)
					num_f4frl += 1
			self.write("\t" + str(counter + 1) + " of " + str(num_follows) + ": " + str(num_f) + " f, " + str(num_frl) + " f+rl, " + str(num_f4f) + " f4f, " + str(num_f4frl) + " f4f+rl" + " ( " + str(errors) + " errors )")


	def getNewFollowFromDB(self, alreadyFollowed):
		blogname = self.getAccountName()
		while True:
			follow = self.dbManager.getFollows(blogname,1)
			if follow == []:
				self.writeError("Error: no follow in DB!")
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
			tag = self.randomF4F()
			follow = self.getTaggedRecentInsta(tag, 1)
			if follow == None:
				self.writeError("Error: 'None' response for find recent media tagged '" + tag + "'")
				num_errors += 1
				if num_errors >= max_errors:
					self.writeError("Error: max num errors reached for getNewFollowFromSearch!")
					return False, None
				else:
					self.waitInsta(little=True)
			elif follow == []:
				self.writeError("Error: cannot find recent media tagged '" + tag + "'")
				return False, None
			elif not follow[0]['userID'] in alreadyFollowed:
				return True, follow[0]['userID']
			else:
				num_errors += 1
				if num_errors >= max_errors:
					self.writeError("Error: max num errors reached for getNewFollowFromSearch!")
					return False, None
				else:
					self.waitInsta(little=True)



	def followAndRandomLike(self, follow, isDump, isF4F = False):
		if isDump:
			if isF4F:
				self.write("f4f and random like:")
			else:
				self.write("follow and random like:")
			self.write(str(follow)) 
		self.followInsta(follow)
		self.randomMediaLikeInsta(follow)
		if isF4F:
			self.addStatistics(follow, 'f4f+rl')
		else:
			self.deleteFollowFromDB(follow)
			self.addStatistics(follow, 'f+rl')


	def justFollow(self, follow, isDump, isF4F = False):
		if isDump:
			if isF4F:
				self.write("just f4f:")
			else:
				self.write("just follow:")
			self.write(str(follow))
		self.followInsta(follow)
		if isF4F:
			self.addStatistics(follow, 'f4f')
		else:
			self.deleteFollowFromDB(follow)
			self.addStatistics(follow, 'f')


	def followInsta(self, blog2follow):
		self.post_insta_request({'action': 'follow_insta', 'user': str(blog2follow)})
		self.followingList.append(blog2follow)
		self.waitInsta()


	def unfollowSocial(self, blog2unfollow):
		self.post_insta_request({'action': 'unfollow_insta', 'user': str(blog2unfollow)})
		self.waitInsta()


	def likeSocial(self, num_likes, isDump):
		blogname = self.getAccountName()
		num_l4l = 0
		num_l4lf = 0
		num_l4lrl = 0
		num_l4lfrl = 0
		num_lfrl = 0
		num_lf = 0
		num_lrl = 0
		num_l = 0
		num_rl = 0
		errors = 0
		for counter in range(0,num_likes):
			seed = random.random()
			tfl = self.statistics['timer_like_prob']
			if seed <= (tfl['l4l'] + tfl['l4l+f'] + tfl['l4l+rl'] + tfl['l4l+f+rl']):
				tag = self.randomL4L()
				self.write("\tGet recent media with tag '" + tag + "'.. ")
				media = self.getTaggedRecentInsta(tag,1)
				if media == None:
					errors += 1
					self.write("\t" + str(counter + 1) + " of " + str(num_likes) + ": " + str(num_l4l) + " l4l, " + str(num_l4lf) + " l4l+f, " + str(num_l4lrl) + " l4l+rl, " + str(num_l4lfrl) + " l4l+f+rl, " + str(num_lfrl) + " l+f+rl, " + str(num_lf) + " l+f, " + str(num_lrl) + " l+rl, " + str(num_l) + " l, " + str(num_rl) + " rl ( " + str(errors) + " errors )")
					continue
				elif media == []:
					self.write("no recent tag for '" + tag + "'!")
					errors += 1
					self.write("\t" + str(counter + 1) + " of " + str(num_likes) + ": " + str(num_l4l) + " l4l, " + str(num_l4lf) + " l4l+f, " + str(num_l4lrl) + " l4l+rl, " + str(num_l4lfrl) + " l4l+f+rl, " + str(num_lfrl) + " l+f+rl, " + str(num_lf) + " l+f, " + str(num_lrl) + " l+rl, " + str(num_l) + " l, " + str(num_rl) + " rl ( " + str(errors) + " errors )")
					continue
				else:
					self.write("ok")
				media = media[0]
				if seed <= tfl['l4l']:
					self.justLike(media, isDump, isL4L = True)
					num_l4l += 1
				elif seed <= tfl['l4l'] + tfl['l4l+f']:
					self.likeAndFollow(media, isDump, isL4L = True)
					num_l4lf += 1
				elif seed <= tfl['l4l'] + tfl['l4l+f'] + tfl['l4l+rl']:
					self.likeAndRandomLike(media, isDump, isL4L = True)
					num_l4lrl += 1
				else:
					self.likeFollowAndRandomLike(media, isDump, isL4L = True)
					num_l4lfrl += 1
			elif seed <= (1 - tfl['rl']):
				seed -= (tfl['l4l'] + tfl['l4l+f'] + tfl['l4l+rl'] + tfl['l4l+f+rl'])
				tag = self.randomTag()
				if tag == "":
					self.write("cannot get random tag!")
					errors += 1
					self.write("\t" + str(counter + 1) + " of " + str(num_likes) + ": " + str(num_l4l) + " l4l, " + str(num_l4lf) + " l4l+f, " + str(num_l4lrl) + " l4l+rl, " + str(num_l4lfrl) + " l4l+f+rl, " + str(num_lfrl) + " l+f+rl, " + str(num_lf) + " l+f, " + str(num_lrl) + " l+rl, " + str(num_l) + " l, " + str(num_rl) + " rl ( " + str(errors) + " errors )")
					continue
				self.write("\tGet recent media with tag '" + tag + "'.. ")
				media = self.getTaggedRecentInsta(tag,1)
				if media == None:
					errors += 1
					self.write("\t" + str(counter + 1) + " of " + str(num_likes) + ": " + str(num_l4l) + " l4l, " + str(num_l4lf) + " l4l+f, " + str(num_l4lrl) + " l4l+rl, " + str(num_l4lfrl) + " l4l+f+rl, " + str(num_lfrl) + " l+f+rl, " + str(num_lf) + " l+f, " + str(num_lrl) + " l+rl, " + str(num_l) + " l, " + str(num_rl) + " rl ( " + str(errors) + " errors )")
					continue
				elif media == []:
					self.write("no recent tag for '" + tag + "'!")
					errors += 1
					self.write("\t" + str(counter + 1) + " of " + str(num_likes) + ": " + str(num_l4l) + " l4l, " + str(num_l4lf) + " l4l+f, " + str(num_l4lrl) + " l4l+rl, " + str(num_l4lfrl) + " l4l+f+rl, " + str(num_lfrl) + " l+f+rl, " + str(num_lf) + " l+f, " + str(num_lrl) + " l+rl, " + str(num_l) + " l, " + str(num_rl) + " rl ( " + str(errors) + " errors )")
					continue
				else:
					self.write("ok")
				media = media[0]
				if seed <= tfl['l+f+rl']:
					self.likeFollowAndRandomLike(media, isDump)
					num_lfrl += 1
				elif seed <= tfl['l+f+rl'] + tfl['l+f']:
					self.likeAndFollow(media, isDump)
					num_lf += 1
				elif seed <= tfl['l+f+rl'] + tfl['l+f'] + tfl['l+rl']:
					self.likeAndRandomLike(media, isDump)
					num_lrl += 1
				else:
					self.justLike(media, isDump)
					num_l += 1
			else:
				could_get, user = self.getNewFollowFromDB([])
				if not could_get:
					self.write("no follow in DB!")
					errors += 1
					self.write("\t" + str(counter + 1) + " of " + str(num_likes) + ": " + str(num_l4l) + " l4l, " + str(num_l4lf) + " l4l+f, " + str(num_l4lrl) + " l4l+rl, " + str(num_l4lfrl) + " l4l+f+rl, " + str(num_lfrl) + " l+f+rl, " + str(num_lf) + " l+f, " + str(num_lrl) + " l+rl, " + str(num_l) + " l, " + str(num_rl) + " rl ( " + str(errors) + " errors )")
					continue
				self.randomLike(user, isDump)
				num_rl += 1
			self.write("\t" + str(counter + 1) + " of " + str(num_likes) + ": " + str(num_l4l) + " l4l, " + str(num_l4lf) + " l4l+f, " + str(num_l4lrl) + " l4l+rl, " + str(num_l4lfrl) + " l4l+f+rl, " + str(num_lfrl) + " l+f+rl, " + str(num_lf) + " l+f, " + str(num_lrl) + " l+rl, " + str(num_l) + " l, " + str(num_rl) + " rl ( " + str(errors) + " errors )")


	def justLike(self, media, isDump, isL4L = False):
		self.likeInsta(media['mediaID'])
		if isL4L:
			self.addStatistics(media['userID'], 'l4l')
			if isDump:
				self.write("l4l")
		else:
			self.addStatistics(media['userID'], 'l')
			if isDump:
				self.write("l")


	def likeAndFollow(self, media, isDump, isL4L = False):
		self.likeInsta(media['mediaID'])
		self.followInsta(media['userID'])
		if isL4L:
			self.addStatistics(media['userID'], 'l4l+f')
			if isDump:
				self.write("l4l+f")
		else:
			self.addStatistics(media['userID'], 'l+f')
			if isDump:
				self.write("l+f")


	def likeAndRandomLike(self, media, isDump, isL4L = False):
		self.likeInsta(media['mediaID'])
		self.randomMediaLikeInsta(media['userID'])
		if isL4L:
			self.addStatistics(media['userID'], 'l4l+rl')
			if isDump:
				self.write("l4l+rl")
		else:
			self.addStatistics(media['userID'], 'l+rl')
			if isDump:
				self.write("l+rl")


	def likeFollowAndRandomLike(self, media, isDump, isL4L = False):
		self.likeInsta(media['mediaID'])
		self.followInsta(media['userID'])
		self.randomMediaLikeInsta(media['userID'])
		if isL4L:
			self.addStatistics(media['userID'], 'l4l+f+rl')
			if isDump:
				self.write("l4l+f+rl")
		else:
			self.addStatistics(media['userID'], 'l+f+rl')
			if isDump:
				self.write("l+f+rl")


	def randomLike(self, userID, isDump):
		self.randomMediaLikeInsta(userID)
		self.deleteFollowFromDB(userID)
		self.addStatistics(userID, 'rl')
		if isDump:
			self.write("rl")


	def likeInsta(self, postID):
		self.post_insta_request({'action': 'like_insta', 'postID': str(postID)})
		self.waitInsta()


	def getFollowersSocial(self, user=None, maxNum=None):
		""" must return dict with users (dict with name for each user) e total_users (total number of Followers of the blog) """
		params = {'action': 'get_followers_insta'}
		if user != None:
			params['userID'] = str(user)
		if maxNum != None:
			params['maxNum'] = maxNum
		followers = self.post_insta_request(params)
		if user == None:
			if followers == None:
				self.write("\t\tGet Followers List.. Error: None response.")
			else:
				self.write("\t\tGet Followers List.. " + str(len(followers)) + "/" + str(self.data['followers']))
		return followers


	def getFollowingsSocial(self, user=None):
		""" must return a list with ID for each user """
		if user == None:
			following = self.post_insta_request({'action': 'get_followings_insta'})
		else:
			following = self.post_insta_request({'action': 'get_followings_insta', 'userID': str(user)})
		self.write("\t\tGet Following List.. " + str(len(following)) + "/" + str(self.data['following']))
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
		if media == None:
			self.writeError("\tError: randomMediaLikeInsta media=None for user '" + str(user) + "'")
		elif media == []:
			self.writeError("\tError: randomMediaLikeInsta media=[] for user '" + str(user) + "'")
		else:
			self.waitInsta(little=True)
			for count in range(0,howMany):
				key = random.randint(0, len(media)-1)
				self.likeInsta(media.pop(key))


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
			print "\t" + tag 
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







