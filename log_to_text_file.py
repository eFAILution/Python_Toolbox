import logging
import logging.handlers
import sys
import os


def get_logger(module_name, logging_path):
    """
    Logs script messages to file
    Parameters
    ---------
    module_name : object
        name of calling module
    logging_path : str
        File path to create/append log to minus 'log' ext.
    Returns
    ---------
    Logging object
    """

    basedir = os.path.dirname(logging_path + ".log")
    if not os.path.exists(basedir):
        os.makedirs(basedir)

    # Add header if this is a new log
    if not os.path.exists(logging_path + ".log"):
        with open(logging_path + ".log", "w") as fh:
            fh.write("Date Time: Level : Module : Message \n")
        new_log = True
    else:
        new_log = False

    logger = logging.getLogger(module_name)
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    # create rotating file handler which logs even debug messages to a
    # max file size of 5MB.Only keeps one backup of each log saved as
    # *.log.1
    fh = logging.handlers.RotatingFilehandler(
        logging_path + ".log", mode="a", maxBytes=int(5e6), backupCount=1
    )
    # fh = logging.FileHandler (logging_path +'.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    fh_formatter = logging.Formatter(
        "*% (asctime)s : %(levelname)s : %(name)s : %(message)s"
    )
    ch_formatter = logging.Formatter("% (message)s")
    ch.setFormatter(ch_formatter)
    fh.setFormatter(fh_formatter)
    # add the handlers to logger
    logger.addHandler(ch)
    logger .addHandler(fh)
    return logger


"""
HOW TO USE:
from log_to_text_file import get_logger as logger
logging_path = <full log file path as string› #'./.logs/snuffy.log'
log = logger (__name_
_, logging_path) #_
_name_ is python built-in for module name
log.debug('This is an DEBUG entry')
log.info('This is an INFO entry')
log .warning('This is an WARNING entry')
log.critical ('This is an CRITICAL entry')
"""
