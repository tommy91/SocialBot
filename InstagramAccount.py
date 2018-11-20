import os
import pickle

class InstagramAccount(Account):

	percF4F = 1/2
	percNotF4F = 1/2

	MAX_RETRIEVED_MEDIA = 10
	MAX_RETRIEVED_LIKE = 10
	MAX_RETRIEVED_COMMENTS = 10

	FSTATS_TRASH_TIME = 60*60*24*20		# 20 days

	MIN_TIME_BETWEEN_ACTIONS = 30		# seconds
	MAX_TIME_BETWEEN_ACTIONS = 40		# seconds 


	def __init__(self, accounts, account, tags, blogs):
		print "Creating new InstagramAccount object.."
		super().__init__(accounts, account['ID'], account['Mail'], account['Type'])
		self.username = account['Username']
		self.password = account['Password']
		self.tags = Utils.tags2list(tags)
		self.blogs = Utils.blogs2list(blogs)
		self.accountName = account['Name']
		self.data = self.initData()
		self.num_post_xd = int(account['PostXD'])
		self.num_follow_xd = int(account['FollowXD'])
		self.num_like_xd = int(account['LikeXD'])
		self.num_post_xt = int(account['PostXT'])
		self.num_follow_xt = int(account['FollowXT'])
		self.num_like_xt = int(account['LikeXT'])
		status = self.STATUS_STOP
		self.loadStatistics()
		print "InstagramAccount object created."


	def initData(self):
		return {'private': "not available",
				'following': "not available",
				'followers': "not available",
				'messages': "not available",
				'name': "not available",
				'posts': "not available",
				'usertags': "not available"
				}


	def getAccountName(self):
		return self.accountName


	def getSocialName(self):
		return "insta"


	def loadStatistics(self):
		self.output.write("Load Statistics..")
		if self.accountName is None:
			print "Error: account name = None"
		elif self.accountName == "not available":
			print "Error: account name = 'not available'"
		elif not os.path.exists("dump/" + self.accountName + ".p"):
			print "no dump for '" + self.accountName + "'"
			print "Creating statistics.. "
			self.initStatistics()
			print "ok"
		else:
			self.statistics = pickle.load(open("dump/" + self.accountName + ".p","rb"))


	def initStatistics(self):
		self.statistics = { 'timer_follow_match': {	'f+rl': 1, 'f': 1 },
							'timer_follow_tot':   { 'f+rl': 1, 'f': 1 },
							'timer_follow_succ':  {	'f+rl': float(1), 'f': float(1) },
							'timer_follow_prob':  {	'f+rl': 1/float(4), 'f': 1/float(4) },
							'timer_like_match':   { 'l+f+rl': 1, 'l+f': 1, 'l+rl': 1, 'l': 1, 'rl': 1 },
							'timer_like_tot': 	  { 'l+f+rl': 1, 'l+f': 1, 'l+rl': 1, 'l': 1, 'rl': 1 },
							'timer_like_succ': 	  { 'l+f+rl': float(1), 'l+f': float(1), 'l+rl': float(1), 'l': float(1), 'rl': float(1) },
							'timer_like_prob': 	  { 'l+f+rl': 1/float(9), 'l+f': 1/float(9), 'l+rl': 1/float(9), 'l': 1/float(9), 'rl': 1/float(9) }
							}
		self.dumpStatistics()


	def dumpStatistics(self):
		pickle.dump(self.statistics,open("dump/" + self.accountName + ".p","wb"))


	def updateMatchStatistics(self, group, action):
		self.statistics[group + "_match"][action] += 1
		self.updateSuccProbStatistics(group, action)


	def updateMatchesStatistics(self):
		bn = self.getAccountName()
		for follow in self.followersList:
			fstats = self.dbManager.getFstats(bn,follow)
			if fstats != []:
				for fstat in fstats:
					if fstat['action'][0] = 'f':
						self.updateMatchStatistics('timer_follow', fstat['action'])
					else:
						self.updateMatchStatistics('timer_follow', fstat['action'])
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


	def post_insta_request(self, post_data):
		post_data['username'] = self.username
		post_data['password'] = self.password
		return Utils.post_request(post_data)


	def checkResponse(self, res):
		"Check if there is an error in response"
		if res != None:
			return True
		else:
			return False


	def updateAccount(self):
		try:
			ibi = self.post_insta_request({'action': 'get_insta_blog_self_info'})
			if self.checkResponse(ibi):
				self.data['private'] = ibi['private']
				self.data['following'] = ibi['following']
				self.data['followers'] = ibi['follower']
				self.data['messages'] = ibi['message']
				self.data['name'] = ibi['name']
				self.data['posts'] = ibi['post']
				self.data['usertags'] = ibi['usertags']
			else:
				self.output.write("Error: cannot update " + self.getAccountName() + ".\n")
		except Exception, msg:
			self.output.write("\tUpdate Error on get_insta_blog_self_info: " + str(msg) + "\n")
						


	def updateBlogData(self, timersTime):
		self.output.write("\tUpdate " + self.data['name'] + ".. ")
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
		up_res = post_request(post_data_up)
		if up_res != None:
			self.updateStatus()
			self.output.write("end of update.\n")


	def updateUpOp(self, newAccount):
		self.username = newAccount['Username']
		self.password = newAccount['Password']
		super().updateUpOp(newAccount)


	def copyBlog(self, blog_to_copy, limitMax, counter):
		self.output.write("Method 'copyBlog' not implemented for Instagram account!\n")


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

		self.output.write("\tCalcule timers for " + self.getAccountName() + ":\n")
		# self.timer_post = int((24*60*60/(self.num_post_xd/self.num_post_xt))+0.5)
		# self.output.write("\t\tpost every " + seconds2timeStr(self.timer_post) + "\n")
		self.output.write("\t\tnever post\n")
		self.timer_follow = int((24*60*60/nf)+0.5)
		self.output.write("\t\tfollow every " + seconds2timeStr(self.timer_follow) + "\n")
		self.timer_like = int((24*60*60/nl)+0.5)
		self.output.write("\t\tlike every " + seconds2timeStr(self.timer_like) + "\n")


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
		self.output.write("\t   check #follow.. ")
		if follows >= self.num_follow_xt:
			self.output.write("found " + str(follows) + ", ok\n")
		else:
			self.output.write("found " + str(follows) + ", needed at least " + str(self.num_follow_xt) + "\n")
			self.searchNewFollows(self.num_follow_xt-follows)


	def searchNewFollows(self, num_follows):
		num_following_blogs = len(self.blogs)
		if num_following_blogs >= num_follows:
			followXblog = 1
		else:
			followXblog = int(num_follows/num_following_blogs)+1
		self.output.write("\t      Getting follows..\n")
		for blog in self.blogs:
			counter = 0
			blog_id = getIdByUsernameInsta(blog)
			followers = self.getFollowersSocial(user=blog_id, maxNum=followXblog)
			for follow in followers:
				if (not follow in self.followersList) and (not follow in self.followingList):
					self.addFollowToDB(follow)
					counter += 1
					self.output.write("\r\t         from " + blog + ".. " + str(counter))
			print ""
			self.waitInsta(little=True)
		tag = self.randomTag()
		if self.MAX_RETRIEVED_COMMENTS + self.MAX_RETRIEVED_LIKE >= num_follows:
			popularPosts = 1
		else:
			popularPosts = int(num_follows/(self.MAX_RETRIEVED_COMMENTS + self.MAX_RETRIEVED_LIKE))+1
		counterMedia = 0
		counterLikers = 0
		counterComments = 0
		media = self.getTaggedPopularInsta(tag, popularPosts)
		for post in media:
			if (not post['userID'] in self.followingList) and (not post['userID'] in self.followersList):
				self.addFollowToDB(post['userID'])
				counterMedia += 1
				self.output.write("\r\t         from posts: " + str(counterMedia) + ", from likes: " + str(counterLikers) + ", from comments: " + str(counterComments))
			self.waitInsta(little=True)
			likers = self.getMediaLikersInsta(post['mediaID'], self.MAX_RETRIEVED_LIKE)
			for liker in likers: 
				if (not liker in self.followingList) and (not liker in self.followersList):
					self.addFollowToDB(liker)
					counterLikers += 1
					self.output.write("\r\t         from posts: " + str(counterMedia) + ", from likes: " + str(counterLikers) + ", from comments: " + str(counterComments))
			self.waitInsta(little=True)
			comments = self.getMediaCommentsInsta(post['mediaID'], self.MAX_RETRIEVED_COMMENTS)
			for comment in comments: 
				if (not comment in self.followingList) and (not comment in self.followersList):
					self.addFollowToDB(comment)
					counterComments += 1
					self.output.write("\r\t         from posts: " + str(counterMedia) + ", from likes: " + str(counterLikers) + ", from comments: " + str(counterComments))
			self.waitInsta(little=True)
		print ""


	def postSocial(self, post):
		self.output.write("Method 'post' not implemented for Instagram account!\n")


	def followSocial(self, num_follows, isDump):
		blogname = self.getAccountName()
		alreadyFollowed = []
		num_f = 0
		num_f4f = 0
		num_frl = 0
		num_f4frl = 0
		for counter in range(0,num_follows):
			seed = random.random()
			tfp = self.statistics['timer_follow_prob']
			if seed <= (tfp['f+rl'] + tfp['f']):
				follow = self.getNewFollowFromDB(alreadyFollowed)
				alreadyFollowed.append(follow)
				if seed <= tfp['f+rl']:
					self.followAndRandomLike(follow, isDump)
				else:
					self.justFollow(follow, isDump)
			else:
				follow = self.getNewFollowFromSearch(alreadyFollowed)
				alreadyFollowed.append(follow)
				if seed <= (tfp['f+rl'] + tfp['f'] + tfp['f4f']):
					self.justFollow(follow, isDump, isF4F = True)
				else:
					self.followAndRandomLike(follow, isDump, isF4F = True)
			self.output.write("\r\t" + str(num_f) + " f, " + str(num_frl) + " f+rl, " + str(num_f4f) + " f4f, " + str(num_f4frl) + " f4f+rl of " + str(num_follows))


	def getNewFollowFromDB(self, alreadyFollowed):
		max_errors = 10
		num_errors = 0
		while True:
			follow = self.dbManager.getFollows(blogname,1)
			if not follow in alreadyFollowed:
				return follow
			else:
				args = (follow,blogname)
				self.dbManager.delete("Follow",args)
				num_errors += 1
				if num_errors >= max_errors:
					self.output.write("Error: max num errors reached for getNewFollowFromDB for '" + blogname + "'\n")
					break


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
		while True:
			tag = self.randomF4F()
			follow = self.getTaggedRecentInsta(tag, 1)
			if not follow['userID'] in alreadyFollowed:
				return follow['userID']
			else:
				num_errors += 1
				if num_errors >= max_errors:
					self.output.write("Error: max num errors reached for getNewFollowFromDB for '" + blogname + "'\n")
					break
				else:
					self.waitInsta(little=True)



	def followAndRandomLike(self, follow, isDump, isF4F = False):
		if isDump:
			if isF4F:
				print "f4f and random like:"
			else:
				print "follow and random like:"
			print follow 
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
				print "just f4f:"
			else:
				print "just follow:"
			print follow 
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


	def likeSocial(self, num_likes):
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
		for counter in range(0,num_follows):
			seed = random.random()
			tfl = self.statistics['timer_like_prob']
			if seed <= (tfl['l4l'] + tfl['l4l+f'] + tfl['l4l+rl'] + tfl['l4l+f+rl']):
				tag = self.randomL4L()
				media = self.getTaggedRecentInsta(tag,1)
				if seed <= tfl['l4l']:
					self.justLike(media, isL4L = True)
				elif seed <= tfl['l4l'] + tfl['l4l+f']:
					self.likeAndFollow(media, isL4L = True)
				elif seed <= tfl['l4l'] + tfl['l4l+f'] + tfl['l4l+rl']:
					self.likeAndRandomLike(media, isL4L = True)
				else:
					self.likeFollowAndRandomLike(media, isL4L = True)
			elif seed <= (1 - tfl['rl']):
				seed -= (tfl['l4l'] + tfl['l4l+f'] + tfl['l4l+rl'] + tfl['l4l+f+rl'])
				tag = self.randomTag()
				media = self.getTaggedRecentInsta()
				if seed <= tfl['l+f+rl']:
					self.likeFollowAndRandomLike(media)
				elif seed <= tfl['l+f+rl'] + tfl['l+f']:
					self.likeAndFollow(media)
				elif seed <= tfl['l+f+rl'] + tfl['l+f'] + tfl['l+rl']:
					self.likeAndRandomLike(media)
				else:
					self.justLike(media)
			else:
				user = self.getNewFollowFromDB([])
				self.randomLike(user)
			self.output.write("\r\t" + str(num_l4l) + " l4l, " + str(num_l4lf) + " l4l+f, " + str(num_l4lrl) + " l4l+rl, " + str(num_l4lfrl) + " l4l+f+rl, " + str(num_lfrl) + " l+f+rl, " + str(num_lf) + " l+f, " + str(num_lrl) + " l+rl, " + str(num_l) + " l, " + str(num_rl) + " rl of " + str(num_follows))


	def justLike(self, media, isL4L = False):
		self.likeInsta(media['mediaID'])
		if isL4L:
			self.addStatistics(media['userID'], 'l4l')
		else:
			self.addStatistics(media['userID'], 'l')


	def likeAndFollow(self, media, isL4L = False):
		self.likeInsta(media['mediaID'])
		self.followInsta(media['userID'])
		if isL4L:
			self.addStatistics(media['userID'], 'l4l+f')
		else:
			self.addStatistics(media['userID'], 'l+f')


	def likeAndRandomLike(self, media, isL4L = False):
		self.likeInsta(media['mediaID'])
		self.randomMediaLikeInsta(media['userID'])
		if isL4L:
			self.addStatistics(media['userID'], 'l4l+rl')
		else:
			self.addStatistics(media['userID'], 'l+rl')


	def likeFollowAndRandomLike(self, media, isL4L = False):
		self.likeInsta(media['mediaID'])
		self.followInsta(media['userID'])
		self.randomMediaLikeInsta(media['userID'])
		if isL4L:
			self.addStatistics(media['userID'], 'l4l+f+rl')
		else:
			self.addStatistics(media['userID'], 'l+f+rl')


	def randomLike(self, userID):
		self.randomMediaLikeInsta(userID)
		self.deleteFollowFromDB(userID)
		self.addStatistics(userID, 'rl')


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
		return self.post_insta_request(params)


	def getFollowingsSocial(self, user=None):
		""" must return a list with ID for each user """
		if user == None:
			return self.post_insta_request({'action': 'get_followings_insta'})
		else:
			return self.post_insta_request({'action': 'get_followings_insta', 'userID': str(user)})


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
		self.waitInsta(little=True)
		for count in range(0,howMany):
			key = random.randint(0, len(media)-1)
			self.likeInsta(media.pop(key))


	def getIdByUsernameInsta(self, user):
		return self.post_insta_request({'action': 'get_id_by_username', 'user': str(user)})[0]







