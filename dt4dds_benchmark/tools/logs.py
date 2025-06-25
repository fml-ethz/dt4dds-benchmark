import logging
import rich
from rich.logging import RichHandler

def setup_console(level=logging.INFO):
    handler = RichHandler(rich_tracebacks=True, tracebacks_suppress=[rich])

    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(handler)

ACTIVE_LOGFILES = {}
def setup_logfile(filepath, level=logging.INFO):
    handler = logging.FileHandler(filepath)
    handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s][%(funcName)s]: %(message)s'))

    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(handler)
    global ACTIVE_LOGFILES
    ACTIVE_LOGFILES[filepath] = handler
logging.setup_logfile = setup_logfile

def remove_logfile(filepath):
    global ACTIVE_LOGFILES
    handler = ACTIVE_LOGFILES.pop(filepath)
    logger = logging.getLogger()
    logger.removeHandler(handler)
logging.remove_logfile = remove_logfile