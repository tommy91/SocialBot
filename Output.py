import logging

from Settings import LOGFILE_PATH


class Output:


	def __init__(self, logname):
		self.infoLog = self.setup_logger(logname, LOGFILE_PATH + logname)
		self.errorLog = self.setup_logger('error_' + logname, LOGFILE_PATH + logname, level=logging.DEBUG)


	def setup_logger(self, name, log_file, level=logging.INFO):
	    """Function setup as many loggers as you want"""
	    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%y %H:%M:%S')
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

