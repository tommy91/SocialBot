import logging

from Settings import LOGFILE_ERROR


class Output:


	def __init__(self, logpath):
		self.logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO, datefmt='%m/%d/%y %H:%M:%S', filename=logpath)
		self.loggingError.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG, datefmt='%m/%d/%y %H:%M:%S', filename=LOGFILE_ERROR)


	def write(self, res):
		self.logging.info(res)


	def writeError(self, res):
		self.logging.error(res)
		self.loggingError.error(res)

