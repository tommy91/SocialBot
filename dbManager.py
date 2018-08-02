#!/usr/bin/python
import os
import sqlite3
import threading

import Utils
import Output
import Settings


class DbManager:


	dbName = "SocialDB.db"
	dbSchema = "dbSchema.sql"


	def __init__(self, dbName=None, dbSchema=None):
		self.output = Output.Output("db.log")
		if dbName != None:
			self.dbName = dbName
		if dbSchema != None:
			self.dbSchema = dbSchema


	def tryDBConnection(self):
		"Look for database"
		self.output.write("Look for local DB (" + self.dbName + ").. ")
		if (not os.path.exists(self.dbName)):
			print "not in path"
			self.initDB()
		else:
			print "already in path!"


	def initDB(self):
		self.output.write("\tCreating database:")
		db = self.connectDB()
		c = db.cursor() 
		self.output.write("\Setup tables.. ")
		with open(dbSchema, 'rt') as f:
			schema = f.read()
		db.executescript(schema)
		self.output.write("ok\n")
		self.disconnectDB(db)
		self.output.write("\tDatabase created.\n")


	def connectDB(self, silent=False):
		"Connect to database"
		if not silent:
			self.output.write("\tConnecting to database.. ")
		db = sqlite3.connect(self.dbName)
		db.isolation_level = None
		db.row_factory = sqlite3.Row
		if not silent:
			self.output.write("connected!\n")
		return (db)


	def disconnectDB(self, db, silent=False):
		"Disconnect from database"
		if not silent:
			self.output.write("\tDisconnecting from database.. ")
		db.close()
		if not silent:
			self.output.write("disconnected!\n")
		

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
				c.execute('INSERT INTO Fstats VALUES (?,?,?,?,?)',args)
		except sqlite3.IntegrityError, msg:
			self.output.writeErrorLog("   Error" + str(msg) + "\n")	
		else: 
			if not silent:
				self.output.writeLog("   Created new entry in " + table + " table.\n")
		self.disconnectDB(db,silent)


	def addList(self, table, argsList, silent=True):
		db = self.connectDB(silent)
		c = db.cursor() 
		c.execute("begin")
		try:
			if table == "PostsLikes":
				c.executemany('INSERT INTO PostsLikes VALUES (?,?,?,?,?)',argsList)
			elif table == "Follow":
				c.executemany('INSERT INTO Follow VALUES (?,?,?)',argsList)
			elif table == "Following":
				c.executemany('INSERT INTO Following VALUES (?,?,?,?)',argsList)
			elif table == "Fstats":
				c.executemany('INSERT INTO Fstats VALUES (?,?,?,?,?)',argsList)
		except sqlite3.IntegrityError, msg:
			c.execute("rollback")
			self.output.writeErrorLog("   Error" + str(msg) + "\n")	
		else: 
			c.execute("commit")
			if not silent:
				self.output.writeLog("   Created new entry in " + table + " table.\n")
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
			self.output.writeErrorLog("\tError" + str(msg) + "\n")
		else:
			if not silent:
				if rows > 0:
					self.output.writeLog("\tDeleted " + str(rows) + " from " + table + "\n")
				else:
					self.output.writeLog("\tThat entry does not exist in " + table + "!\n")
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
			self.output.writeErrorLog("\tError" + str(msg) + "\n")
		else:
			if not silent:
				if rows > 0:
					self.output.writeLog("\tDeleted " + str(rows) + " from " + table + "\n")
				else:
					self.outout.writeLog("\tThat entry does not exist in " + table + "!\n")
		self.disconnectDB(db,silent)


	def deleteFstatsTrash(self, blogname, time, silent=True):
		db = self.connectDB(silent)
		c = db.cursor()
		rows = 0 
		try:
			rows = c.execute('DELETE FROM Fstats WHERE myBlog = "' + blogname + '" AND time<=' + str(time)).rowcount
		except sqlite3.IntegrityError, msg:
			self.output.writeErrorLog("\tError" + str(msg) + "\n")
		else:
			if not silent:
				if rows > 0:
					self.output.writeLog("\tDeleted " + str(rows) + " from Fstats\n")
				else:
					self.output.writeLog("\tThat entry does not exist in Fstats!\n")
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
			self.output.writeErrorLog("\tError" + str(msg) + "\n")
		else:
			if not silent:
				if rows > 0:
					self.output.writeLog("\tUpdated " + str(rows) + " from " + table + "\n")
				else:
					self.output.writeLog("\tThat entry does not exist in " + table + "!\n")
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
			self.output.writeErrorLog("\tError" + str(msg) + "\n")
		else:
			if not silent:
				if rows > 0:
					self.output.writeLog("\tUpdated " + str(rows) + " from " + table + "\n")
				else:
					self.output.writeLog("\tThat entry does not exist in " + table + "!\n")
		self.disconnectDB(db,silent)


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
			self.output.writeLog("\tCounting entries in " + tableName + " database.. ")
		c.execute(query)
		if not silent:
			self.output.writeLog("\tdone!")
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
			self.output.writeLog("\tDownload data from " + tableName + " database.. ")
		c.execute(query)
		if not silent:
			self.output.writeLog("\tdone!\n")
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
			self.output.writeLog("\tDownload data from " + tableName + " database.. ")
		c.execute(query)
		if not silent:
			self.output.writeLog("\tdone!\n")
		result = c.fetchall()
		self.disconnectDB(db,silent)
		return result


	def execute_get(self, query, silent, tableName):
		db = self.connectDB(silent)
		c = db.cursor()
		if not silent:
			self.output.writeLog("\tDownload data from " + tableName + " database.. ")
		c.execute(query)
		if not silent:
			self.output.writeLog("\tdone!\n")
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



