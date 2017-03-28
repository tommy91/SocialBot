#!/usr/bin/python
import sqlite3
import sys
import time
import threading
import datetime

from SocialBot import write, writeln


dbName = "SocialDB.db"


def connectDB(silent=False):
	"Connect to database"
	if not silent:
		write("\tConnecting to database.. ")
	db = sqlite3.connect(dbName)
	db.isolation_level = None
	db.row_factory = sqlite3.Row
	if not silent:
		write("connected!\n")
	return (db)


def disconnectDB(db, silent=False):
	"Disconnect from database"
	if not silent:
		write("\tDisconnecting from database.. ")
	db.close()
	if not silent:
		write("disconnected!\n")


def createTable(db, q):
	try:
	    db.execute(q)
	except sqlite3.OperationalError, msg:
	    write("Error: " + str(msg))
	    return False
	else:
		write("Done.\n")
		return True

def setupTables(db):
	"Setup Accounts table on database 'db'."
	write("\n\tSetup Tables:\n")
	write("\tPostsLikes Table.. ")
	if not createTable(db, "CREATE TABLE PostsLikes (id text, reblogKey text, sourceBlog text, myBlog text, time time)"):
		return False
	write("\tFollow Table.. ")
	if not createTable(db, "CREATE TABLE Follow (sourceBlog text, myblog text, time time)"):
		return False
	write("\tSetup Tables Complete!\n\n")
  		

def add(table,args,silent=True):
	db = connectDB(silent)
	c = db.cursor() 
	try:
		if table == "PostsLikes":
			c.execute('INSERT INTO PostsLikes VALUES (?,?,?,?,?)',args)
		elif table == "Follow":
			c.execute('INSERT INTO Follow VALUES (?,?,?)',args)
	except sqlite3.IntegrityError, msg:
	    write("   Error" + str(msg) + "\n")	
	else: 
		if not silent:
			write("   Created new entry in " + table + " table.\n")
	disconnectDB(db,silent)


def delete(table,args,silent=True):
	db = connectDB(silent)
	c = db.cursor()
	rows = 0 
	try:
		if table == "PostsLikes":
			rows = c.execute('DELETE FROM PostsLikes WHERE id = ? AND myBlog = ?',args).rowcount
		elif table == "Follow":
			rows = c.execute('DELETE FROM Follow WHERE sourceBlog = ? AND myBlog = ?',args).rowcount
	except sqlite3.IntegrityError, msg:
	    write("\tError" + str(msg) + "\n")
	else:
		if not silent:
			if rows > 0:
				write("\tDeleted " + str(rows) + " from " + table + "\n")
			else:
				write("\tThat entry does not exist in " + table + "!\n")
	disconnectDB(db,silent)


def initDB():
	write("\tCreating database:\n")
	db = connectDB()
	c = db.cursor() 
	setupTables(c)
	disconnectDB(db)


def get(tableName,fields=None,silent=False):
	if fields != None:
		return execute_get('SELECT ' + fields + ' FROM ' + tableName, silent, tableName)
	else:
		return execute_get('SELECT * FROM ' + tableName, silent, tableName)


def count(tableName,silent=False):
	return executeCount('SELECT * FROM ' + tableName, silent, tableName)


def countPost(blogname,silent=True):
	return executeCount('SELECT * FROM PostsLikes WHERE myBlog = "' + blogname + '" GROUP BY id', silent, "PostsLikes")


def countFollow(blogname,silent=True):
	return executeCount('SELECT * FROM Follow WHERE myBlog = "' + blogname + '" GROUP BY sourceBlog', silent, "Follow")


def countAllPost(silent=True):
	return executeCount('SELECT * FROM PostsLikes GROUP BY id', silent, "PostsLikes")


def countAllFollow(silent=True):
	return executeCount('SELECT * FROM Follow GROUP BY sourceBlog', silent, "Follow")


def executeCount(query, silent, tableName):
	db = connectDB(silent)
	c = db.cursor()
	if not silent:
		write("\tCounting entries in " + tableName + " database.. ")
	c.execute(query)
	if not silent:
		write("done!\n")
	rows = len(c.fetchall())
	disconnectDB(db,silent)
	return rows


def getPosts(blogname, limit, silent=True):
	return execute_get('SELECT * FROM PostsLikes WHERE myBlog = "' + blogname + '" GROUP BY id ORDER BY time LIMIT ' + str(limit), silent, "PostsLikes")


def getFollows(blogname, limit, silent=True):
	return execute_get('SELECT * FROM Follow WHERE myBlog = "' + blogname + '" GROUP BY sourceBlog ORDER BY time LIMIT ' + str(limit), silent, "Follow")


def execute_get(query, silent, tableName):
	db = connectDB(silent)
	c = db.cursor()
	if not silent:
		write("\tDownload data from " + tableName + " database.. ")
	c.execute(query)
	if not silent:
		write("done!\n")
	result = c.fetchall()
	disconnectDB(db,silent)
	return result



