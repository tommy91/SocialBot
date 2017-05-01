class Account:

	STATUS_RUN = 1
	STATUS_STOP = 0

	TIMERHALFWINDOW = 10
	LIMITFOLLOW = 4950


	def __init__(self, account_id, mail, account_type):
		self.account_id = int(account_id)
		self.strID = str(account_id)
		self.mail = mail
		self.account_type = int(account_type)


	# todo
	# def write():
	# def post_request():


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
        self.calc_time_post_follow()
        if int(newAccount['Status']) > self.STATUS_RUN:
            if self.status == self.STATUS_STOP:
                post_request({"action": "set_status", "id": self.account_id, "status": self.STATUS_RUN})
                self.runBlog()
            elif self.status == self.STATUS_RUN:
                post_request({"action": "set_status", "id": self.account_id, "status": self.STATUS_STOP})
                self.stopBlog()


    def calc_time_post_follow(self):
	    write("\tCalcule timers for " + self.getAccountName() + ":\n")
	    self.timer_post = int((24*60/(self.num_post_xd/self.num_post_xt))+0.5)
	    write("\t\tpost every " + str(self.timer_post) + " minutes\n")
	    self.timer_follow = int((24*60/(self.num_follow_xd/self.num_follow_xt))+0.5)
	    write("\t\tfollow every " + str(self.timer_follow) + " minutes\n")
	    self.timer_like = int((24*60/(self.num_like_xd/self.num_like_xt))+0.5)
	    write("\t\tlike every " + str(self.timer_like) + " minutes\n")


	def runBlog(self):
	    global timers, lock, canWrite
	    lock.acquire()
	    prevCanWrite = canWrite
	    canWrite = True
	    writeln("Run " + self.getAccountName() + ":\n")
	    self.calc_time_post_follow()
	    self.check_num_post_follow()
	    if timers == {}:
	        set_update_timer()
	    self.set_post_timer()
	    self.set_follow_timer()
	    self.set_like_timer()
	    write("\t" + self.getAccountName() + " is running.\n")
	    self.status = self.STATUS_RUN
	    self.updateBlogData()
	    # updateStatistics()
	    canWrite = prevCanWrite
	    lock.release()


	def stopBlog(self):
	    global timers, lock, canWrite
	    lock.acquire()
	    prevCanWrite = canWrite
	    canWrite = True
	    writeln("Stop " + self.getAccountName() + ".. \n")
	    self.status = self.STATUS_STOP
	    self.updateBlogData()
	    timers[blog['strID'] + "-post"].cancel()
	    del timers[blog['strID'] + "-post"]
	    timers[blog['strID'] + "-follow"].cancel()
	    del timers[blog['strID'] + "-follow"]
	    timers[blog['strID'] + "-like"].cancel()
	    del timers[blog['strID'] + "-like"]
	    # updateStatistics()
	    write("\t" + self.getAccountName() + " stopped.\n")
	    canWrite = prevCanWrite
	    lock.release()




