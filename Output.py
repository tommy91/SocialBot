import sys
import logging

from Settings import LOGFILE_PATH, LOGFILE_ERROR


class Output:


	def __init__(self, logname):
		self.infoLog = self.setup_info_logger(logname, LOGFILE_PATH + logname + ".log")
		self.errorLog = self.setup_error_logger('error', LOGFILE_ERROR)


	def setup_info_logger(self, name, log_file):
		formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%y %H:%M:%S')
		return self.setup_logger(name, log_file, formatter, logging.INFO)


	def setup_error_logger(self, name, log_file):
		formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(funcName)s: %(message)s', datefmt='%m/%d/%y %H:%M:%S')
		return self.setup_logger(name, log_file, formatter, logging.DEBUG)


	def setup_logger(self, name, log_file, formatter, level):
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
		sys.stdout.write(res))
		sys.stdout.flush()

