#import os
import sys
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger(__name__)
my_logger = logging.getLogger("mylog")
frontend_logger = logging.getLogger("werkzeug")
logger.info('start')

def config_logging(log_file, basic_level, log_file_level, web_server_level, pil_level):
	rfh = RotatingFileHandler(
		filename=log_file,
		mode="a",
		maxBytes= (1024 * 1024)//2,
		backupCount=2,
		encoding=None,
		delay=0,
	)
	rfh.setLevel(log_file_level)
	logging.basicConfig(
		handlers=[logging.StreamHandler(sys.stdout), rfh],
		level=basic_level,
		format="%(asctime)s %(levelname)s %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S",
	)
	frontend_logger.setLevel(web_server_level)
	





#logging config
config_logging("my.log", "DEBUG", "DEBUG","INFO", "INFO")
logger.info('stop')
logger.debug('debug')
logger.error('error')
