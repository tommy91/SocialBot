import os
import sys
import logging

from Settings import LOGFILE_PATH, LOGFILE_ERROR


class Output:


	def __init__(self, logname, subdir=None):
		self.logname = logname
		# setup log directory
		if not os.path.exists(LOGFILE_PATH):
			os.mkdir(LOGFILE_PATH)
		if (subdir is not None) and (not os.path.exists(LOGFILE_PATH + subdir + "/")):
			os.mkdir(LOGFILE_PATH + subdir + "/")
		if subdir is None:
			self.infoLog = self.setupInfoLogger(logname, LOGFILE_PATH + logname)
		else:
			self.infoLog = self.setupInfoLogger(logname, LOGFILE_PATH + subdir + "/" + logname)
		self.errorLog = self.setupErrorLogger('error', LOGFILE_ERROR)


	def getLogName(self):
		return self.logname


	def setupInfoLogger(self, name, log_file):
		formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%y %H:%M:%S')
		return self.setupLogger(name, log_file, formatter, logging.INFO)


	def setupErrorLogger(self, name, log_file):
		formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(funcName)s: %(message)s', datefmt='%m/%d/%y %H:%M:%S')
		return self.setupLogger(name, log_file, formatter, logging.DEBUG)


	def setupLogger(self, name, log_file, formatter, level):
		"""Function setup as many loggers as you want"""
		handler = logging.FileHandler(log_file)        
		handler.setFormatter(formatter)
		logger = logging.getLogger(name)
		logger.setLevel(level)
		logger.addHandler(handler)
		return logger


	def writeLog(self, res):
		self.infoLog.info(res)


	def writeErrorLog(self, res):
		self.infoLog.error(res)
		self.errorLog.error(res)


	def write(self, res):
		sys.stdout.write(res)
		sys.stdout.flush()

