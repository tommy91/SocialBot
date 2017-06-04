#!/usr/bin/python
import sqlite3


class DbManager:


	dbName = "SocialDB.db"


	def __init__(self, output, dbName=None):
		self.write = output.write
		self.writeln = output.writeln
		if dbName != None:
			self.dbName = dbName


	def connectDB(self, silent=False):
		"Connect to database"
		if not silent:
			self.write("\tConnecting to database.. ")
		db = sqlite3.connect(self.dbName)
		db.isolation_level = None
		db.row_factory = sqlite3.Row
		if not silent:
			self.write("connected!\n")
		return (db)


	def disconnectDB(self, db, silent=False):
		"Disconnect from database"
		if not silent:
			self.write("\tDisconnecting from database.. ")
		db.close()
		if not silent:
			self.write("disconnected!\n")


	def createTable(self, db, q):
		try:
			db.execute(q)
		except sqlite3.OperationalError, msg:
			self.write("Error: " + str(msg))
			return False
		else:
			self.write("Done.\n")
			return True

	def setupTables(self, db):
		"Setup Accounts table on database 'db'."
		self.write("\n\tSetup Tables:\n")
		self.write("\tPostsLikes Table.. ")
		if not self.createTable(db, "CREATE table if not exists PostsLikes (id text, reblogKey text, sourceBlog text, myBlog text, time time)"):
			return False
		self.write("\tFollow Table.. ")
		if not self.createTable(db, "CREATE table if not exists Follow (sourceBlog text, myblog text, time time)"):
			return False
		self.write("\tFollowing Table.. ")
		if not self.createTable(db, "CREATE table if not exists Following (myBlog text, followedBlog text, isFollowingBack boolean, time time)"):
			return False
		self.write("\tFstats Table.. ")
		if not self.createTable(db, "CREATE table if not exists Fstats (myBlog text, followedBlog text, action text, time time)"):
			return False
		self.write("\tSetup Tables Complete!\n\n")
		

	def add(self, table, args, silent=True):
		db = self.connectDB(silent)
		c = db.cursor() 
		try:
			if table == "PostsLikes":
				c.execute('INSERT INTO PostsLikes VALUES (?,?,?,?,?)',args)
			elif table == "Follow":
				c.execute('INSERT INTO Follow VALUES (?,?,?)',args)
			elif table == "Following":
				c.execute('INSERT INTO Following VALUES (?,?,?,?)',args)
			elif table == "Fstats":
				c.execute('INSERT INTO Fstats VALUES (?,?,?,?)',args)
		except sqlite3.IntegrityError, msg:
			self.write("   Error" + str(msg) + "\n")	
		else: 
			if not silent:
				self.write("   Created new entry in " + table + " table.\n")
		self.disconnectDB(db,silent)


	def addList(self, table, argsList, silent=True):
		db = self.connectDB(silent)
		c = db.cursor() 
		while argsList != []:
			try:
				if table == "PostsLikes":
					c.execute('INSERT INTO PostsLikes VALUES (?,?,?,?,?)',argsList.pop())
				elif table == "Follow":
					c.execute('INSERT INTO Follow VALUES (?,?,?)',argsList.pop())
				elif table == "Following":
					c.execute('INSERT INTO Following VALUES (?,?,?,?)',argsList.pop())
				elif table == "Fstats":
					c.execute('INSERT INTO Fstats VALUES (?,?,?,?)',argsList.pop())
			except sqlite3.IntegrityError, msg:
				self.write("   Error" + str(msg) + "\n")	
			else: 
				if not silent:
					self.write("   Created new entry in " + table + " table.\n")
		self.disconnectDB(db,silent)


	def delete(self, table, args, silent=True):
		db = self.connectDB(silent)
		c = db.cursor()
		rows = 0 
		try:
			if table == "PostsLikes":
				rows = c.execute('DELETE FROM PostsLikes WHERE id = ? AND myBlog = ?',args).rowcount
			elif table == "Follow":
				rows = c.execute('DELETE FROM Follow WHERE sourceBlog = ? AND myBlog = ?',args).rowcount
			elif table == "Following":
				rows = c.execute('DELETE FROM Following WHERE myBlog = ? AND followedBlog = ?',args).rowcount
			elif table == "Fstats":
				rows = c.execute('DELETE FROM Fstats WHERE myBlog = ? AND followedBlog = ?',args).rowcount
		except sqlite3.IntegrityError, msg:
			self.write("\tError" + str(msg) + "\n")
		else:
			if not silent:
				if rows > 0:
					self.write("\tDeleted " + str(rows) + " from " + table + "\n")
				else:
					self.write("\tThat entry does not exist in " + table + "!\n")
		self.disconnectDB(db,silent)


	def deleteAll(self, table, args, silent=True):
		db = self.connectDB(silent)
		c = db.cursor()
		rows = 0 
		try:
			if table == "PostsLikes":
				rows = c.execute('DELETE FROM PostsLikes WHERE myBlog = ?',args).rowcount
			elif table == "Follow":
				rows = c.execute('DELETE FROM Follow WHERE myBlog = ?',args).rowcount
			elif table == "Following":
				rows = c.execute('DELETE FROM Following WHERE myBlog = ?',args).rowcount
			elif table == "Fstats":
				rows = c.execute('DELETE FROM Fstats WHERE myBlog = ?',args).rowcount
		except sqlite3.IntegrityError, msg:
			self.write("\tError" + str(msg) + "\n")
		else:
			if not silent:
				if rows > 0:
					self.write("\tDeleted " + str(rows) + " from " + table + "\n")
				else:
					self.write("\tThat entry does not exist in " + table + "!\n")
		self.disconnectDB(db,silent)


	def deleteFstatsTrash(self, blogname, time, silent=True):
		db = self.connectDB(silent)
		c = db.cursor()
		rows = 0 
		try:
			rows = c.execute('DELETE FROM Fstats WHERE myBlog = "' + blogname + '" AND time<=' + str(time)).rowcount
		except sqlite3.IntegrityError, msg:
			self.write("\tError" + str(msg) + "\n")
		else:
			if not silent:
				if rows > 0:
					self.write("\tDeleted " + str(rows) + " from Fstats\n")
				else:
					self.write("\tThat entry does not exist in Fstats!\n")
		self.disconnectDB(db,silent)


	def update(self, table, args, silent=True):
		db = self.connectDB(silent)
		c = db.cursor()
		rows = 0 
		try:
			if table == "PostsLikes":
				pass
			elif table == "Follow":
				pass
			elif table == "Following":
				rows = c.execute('UPDATE Following SET isFollowingBack = ? WHERE myBlog = ? AND followedBlog = ?',args).rowcount
			elif table == "Fstats":
				pass
		except sqlite3.IntegrityError, msg:
			self.write("\tError" + str(msg) + "\n")
		else:
			if not silent:
				if rows > 0:
					self.write("\tUpdated " + str(rows) + " from " + table + "\n")
				else:
					self.write("\tThat entry does not exist in " + table + "!\n")
		self.disconnectDB(db,silent)


	def updateAll(self, table, args, silent=True):
		db = self.connectDB(silent)
		c = db.cursor()
		rows = 0 
		try:
			if table == "PostsLikes":
				pass
			elif table == "Follow":
				pass
			elif table == "Following":
				rows = c.execute('UPDATE Following SET isFollowingBack = ? WHERE myBlog = ?',args).rowcount
			elif table == "Fstats":
				pass
		except sqlite3.IntegrityError, msg:
			self.write("\tError" + str(msg) + "\n")
		else:
			if not silent:
				if rows > 0:
					self.write("\tUpdated " + str(rows) + " from " + table + "\n")
				else:
					self.write("\tThat entry does not exist in " + table + "!\n")
		self.disconnectDB(db,silent)


	def initDB(self):
		self.write("\tCreating database:\n")
		db = self.connectDB()
		c = db.cursor() 
		self.setupTables(c)
		self.disconnectDB(db)


	def count(self, tableName, silent=False):
		return self.executeCount('SELECT * FROM ' + tableName, silent, tableName)


	def countPost(self, blogname, silent=True):
		return self.executeCount('SELECT * FROM PostsLikes WHERE myBlog = "' + blogname + '" GROUP BY id', silent, "PostsLikes")

	def countLike(self, blogname, silent=True):
		return self.countPost(blogname,silent)


	def countFollow(self, blogname, silent=True):
		return self.executeCount('SELECT * FROM Follow WHERE myBlog = "' + blogname + '" GROUP BY sourceBlog', silent, "Follow")


	def countFollowing(self, blogname, silent=True):
		return self.executeCount('SELECT * FROM Following WHERE myBlog = "' + blogname + '"', silent, "Following")


	def countFstats(self, blogname, silent=True):
		return self.executeCount('SELECT * FROM Fstats WHERE myBlog = "' + blogname + '"', silent, "Fstats")


	def countAllPost(self, silent=True):
		return self.executeCount('SELECT * FROM PostsLikes GROUP BY id', silent, "PostsLikes")


	def countAllFollow(self, silent=True):
		return self.executeCount('SELECT * FROM Follow GROUP BY sourceBlog', silent, "Follow")


	def countAllFollowing(self, silent=True):
		return self.executeCount('SELECT * FROM Following', silent, "Following")


	def countAllFstats(self, silent=True):
		return self.executeCount('SELECT * FROM Fstats', silent, "Fstats")


	def executeCount(self, query, silent, tableName):
		db = self.connectDB(silent)
		c = db.cursor()
		if not silent:
			self.write("\tCounting entries in " + tableName + " database.. ")
		c.execute(query)
		if not silent:
			self.write("done!\n")
		rows = len(c.fetchall())
		self.disconnectDB(db,silent)
		return rows


	def get(self, tableName, fields=None, silent=False):
		if fields != None:
			return self.execute_get('SELECT ' + fields + ' FROM ' + tableName, silent, tableName)
		else:
			return self.execute_get_all('SELECT * FROM ' + tableName, silent, tableName)


	def getPosts(self, blogname, limit, silent=True):
		return self.execute_get_all('SELECT * FROM PostsLikes WHERE myBlog = "' + blogname + '" GROUP BY id ORDER BY time LIMIT ' + str(limit), silent, "PostsLikes")


	def getFollows(self, blogname, limit=None, silent=True):
		if limit == None:
			return self.execute_get_one('SELECT sourceBlog FROM Follow WHERE myBlog = "' + blogname + '" GROUP BY sourceBlog ORDER BY time ', silent, "Follow")
		else:
			return self.execute_get_one('SELECT sourceBlog FROM Follow WHERE myBlog = "' + blogname + '" GROUP BY sourceBlog ORDER BY time LIMIT ' + str(limit), silent, "Follow")


	def getFollowing(self, blogname, silent=True):
		return self.execute_get_one('SELECT followedBlog FROM Following WHERE myBlog = "' + blogname + '" ORDER BY isFollowingBack, time', silent, "Following")


	def getFstats(self, blogname, followedBlog, silent=True):
		return self.execute_get_all('SELECT * FROM Fstats WHERE myBlog = "' + blogname + '" AND followedBlog = "' + followedBlog + '"', silent, "Fstats")


	def getFollowingTrash(self, blogname, time, silent=True):
		return self.execute_get_one('SELECT followedBlog FROM Following WHERE myBlog = "' + blogname + '" AND time<=' + str(time) + ' AND NOT isFollowingBack', silent, "Following")


	def getFstatsTrash(self, blogname, time, silent=True):
		return self.execute_get_one('SELECT followedBlog FROM Fstats WHERE myBlog = "' + blogname + '" AND time<=' + str(time), silent, "Fstats")


	def getTablesNames(self, silent=True):
		return self.execute_get_one("SELECT name FROM sqlite_master WHERE type='table'", silent, "sqlite_master")
	

	def execute_get_all(self, query, silent, tableName):
		db = self.connectDB(silent)
		c = db.cursor()
		if not silent:
			self.write("\tDownload data from " + tableName + " database.. ")
		c.execute(query)
		if not silent:
			self.write("done!\n")
		results = c.fetchall()
		columns = c.description
		col_names = []
		for column in columns:
			name, nk1, nk2, nk3, nk4, nk5, nk6 = column
			col_names.append(name)
		response = []
		for result in results:
			row = {}
			for count in range(0,len(col_names)):
				row[col_names[count]] = result[count]
			response.append(row)
		self.disconnectDB(db,silent)
		return response


	def execute_get_one(self, query, silent, tableName):
		db = self.connectDB(silent)
		db.row_factory = lambda cursor, row: row[0]
		c = db.cursor()
		if not silent:
			self.write("\tDownload data from " + tableName + " database.. ")
		c.execute(query)
		if not silent:
			self.write("done!\n")
		result = c.fetchall()
		self.disconnectDB(db,silent)
		return result


	def execute_get(self, query, silent, tableName):
		db = self.connectDB(silent)
		c = db.cursor()
		if not silent:
			self.write("\tDownload data from " + tableName + " database.. ")
		c.execute(query)
		if not silent:
			self.write("done!\n")
		result = c.fetchall()
		self.disconnectDB(db,silent)
		return result


	def clearDB(self, blogname):
		self.clearPostsLikes4Blog(blogname)
		self.clearFollow4Blog(blogname)
		self.clearFollowing4Blog(blogname)
		self.clearFstats4Blog(blogname)


	def clearTable4blog(self, blogname, table):
		args = (blogname,)
		self.deleteAll(table, args)


	def clearPostsLikes4Blog(self, blogname):
		args = (blogname,)
		self.deleteAll("PostsLikes", args)


	def clearFollow4Blog(self, blogname):
		args = (blogname,)
		self.deleteAll("Follow", args)


	def clearFollowing4Blog(self, blogname):
		args = (blogname,)
		self.deleteAll("Following", args)


	def clearFstats4Blog(self, blogname):
		args = (blogname,)
		self.deleteAll("Fstats", args)



	def setAllFollowingUnfollowed(self, blogname, silent = True):
		args = (False, blogname)
		self.updateAll('Following', args, silent = silent)


	def setFollowingFollowed(self, blogname, follower, isFollowingBack, silent = True):
		args = (isFollowingBack, blogname, follower)
		self.update('Following', args, silent = silent)



