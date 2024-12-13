from logtool import Logger

log = Logger(name='my_log', log_dir='logs').get_logger()
log.setLevel('INFO')
