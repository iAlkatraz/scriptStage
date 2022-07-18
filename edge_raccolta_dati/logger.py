import logging
import sys
import logging.handlers as handlers

logger=logging.getLogger('orchestra_edge')
logger.setLevel(logging.DEBUG)

stdout_file_handler=handlers.RotatingFileHandler('stdout.log',maxBytes=5000000,backupCount=2)
#stdout_file_handler=logging.FileHandler('stdout.log')
stdout_file_formatter=logging.Formatter('%(asctime)s\t-\t%(filename)s\t-\t%(levelname)s: %(message)s')
stdout_file_handler.setFormatter(stdout_file_formatter)
logger.addHandler(stdout_file_handler)

stderr_file_handler=handlers.RotatingFileHandler('stderr.log',maxBytes=5000000,backupCount=2)
#stderr_file_handler=logging.FileHandler('stderr.log')
stderr_file_handler.setLevel(logging.ERROR)
stderr_file_formatter=logging.Formatter('%(asctime)s\t-\t%(filename)s\t-\t%(levelname)s: %(message)s')
stderr_file_handler.setFormatter(stderr_file_formatter)
logger.addHandler(stderr_file_handler)

stdout_console_handler=logging.StreamHandler(sys.stdout)
stdout_console_formatter=logging.Formatter('%(filename)s\t-\t%(levelname)s: %(message)s')
stdout_console_handler.setFormatter(stdout_console_formatter)
logger.addHandler(stdout_console_handler)