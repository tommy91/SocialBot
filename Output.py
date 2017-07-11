import logging

from Settings import LOGFILE_PATH, LOGFILE_ERROR


class Output:


	def __init__(self, logname):
		self.infoLog = self.setup_info_logger(logname, LOGFILE_PATH + logname)
		self.errorLog = self.setup_error_logger('error', LOGFILE_ERROR, level=logging.DEBUG)


	def setup_info_logger(self, name, log_file, level=logging.INFO):
		formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%y %H:%M:%S')
		return self.setup_logger(name, log_file, formatter, level=logging.INFO)


	def setup_error_logger(self, name, log_file, level=logging.INFO):
		formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(funcName)s: %(message)s', datefmt='%m/%d/%y %H:%M:%S')
		return self.setup_logger(name, log_file, formatter, level=logging.INFO)


	def setup_logger(self, name, log_file, formatter, level=logging.INFO):
	    """Function setup as many loggers as you want"""
	    handler = logging.FileHandler(log_file)        
	    handler.setFormatter(formatter)
	    logger = logging.getLogger(name)
	    logger.setLevel(level)
	    logger.addHandler(handler)
	    return logger


	def write(self, res):
		self.infoLog.info(res)


	def writeError(self, res):
		self.infoLog.error(res)
		self.errorLog.error(res)

