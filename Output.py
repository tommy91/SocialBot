import logging

from Settings import LOGFILE_ERROR


formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%y %H:%M:%S')


class Output:


	def __init__(self, logpath):
		self.infoLog = self.setup_logger('infoLog', logpath)
		self.errorLog = self.setup_logger('errorLog', LOGFILE_ERROR, level=logging.DEBUG)


	def setup_logger(name, log_file, level=logging.INFO):
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

