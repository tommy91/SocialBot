import logging

from Settings import LOGFILE_ERROR


class Output:


	def __init__(self, logpath):
		self.infoLog = logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO, datefmt='%m/%d/%y %H:%M:%S', filename=logpath)
		self.errorLog = logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG, datefmt='%m/%d/%y %H:%M:%S', filename=LOGFILE_ERROR)


	def write(self, res):
		self.infoLog.info(res)


	def writeError(self, res):
		self.infoLog.error(res)
		self.errorLog.error(res)

