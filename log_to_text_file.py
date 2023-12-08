import logging
from logging.handlers import RotatingFileHandler
import sys
import os
from colorlog import ColoredFormatter  # Import ColoredFormatter from colorlog


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

    # Set umask so that log file is readable and writable by all
    os.umask(0o000)

    basedir = os.path.dirname(logging_path + ".log")
    if not os.path.exists(basedir):
        os.makedirs(basedir)

    # Add header if this is a new log
    if not os.path.exists(logging_path + ".log"):
        with open(logging_path + ".log", "w", encoding='utf-8') as fh:
            fh.write("Date Time: Level : Module : Message \n")
        new_log = True
    else:
        new_log = False

    logger = logging.getLogger(module_name)
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    # create rotating file handler which logs even debug messages to a
    # max file size of 5MB.Only keeps one backup of each log saved as
    # *.log.1
    fh = RotatingFileHandler(
        logging_path + ".log", mode="a", backupCount=1
    )
    fh.setLevel(logging.DEBUG)

    # Use a ColoredFormatter for console output
    console_formatter = ColoredFormatter(
        "%(log_color)s%(levelname)s%(reset)s %(message_log_color)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'white,bg_green',
            'INFO': 'cyan',
            'WARNING': 'white,bg_yellow',
            'ERROR': 'red',
            'CRITICAL': 'white,bg_red'
        },
        secondary_log_colors={
            'message': {
                'DEBUG': 'green',
                'INFO': 'white',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red'
            },
            'levelname': {
                'DEBUG': 'bold',
                'INFO': 'bold',
                'WARNING': 'bold',
                'ERROR': 'bold',
                'CRITICAL': 'bold'
            }
        }
    )

    # create console handler with a higher log level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    # Set the colored formatter for the console handler
    ch.setFormatter(console_formatter)

    # create formatter and add it to the file handler
    fh_formatter = logging.Formatter(
        "%(asctime)s : %(levelname)s : %(name)s : %(message)s")
    fh.setFormatter(fh_formatter)

    # add the handlers to the logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.debug(f'Logging directory is {basedir}')
    return logger


def set_handler_level(logger, handler_type, level):
    """
    Set the logging level for a specific handler type in a logger.

    Args:
        logger (logging.Logger): The logger object.
        handler_type (type): The type of handler to set the level for.
        level (int): The logging level to set.

    Returns:
        None
    """
    for handler in logger.handlers:
        if isinstance(handler, handler_type):
            handler.setLevel(level)
            break


"""
HOW TO USE:
from log_to_text_file import get_logger as logger
logging_path = <full log file path as string› #'./.logs/snuffy.log'
log = logger (__name__, logging_path)
#__name__ is python built-in for module name
log.debug('This is an DEBUG entry')
log.info('This is an INFO entry')
log .warning('This is an WARNING entry')
log.critical ('This is an CRITICAL entry')
# change console log entries to level DEBUG
set_handler_level(log, logging.StreamHandler, logging.DEBUG)
"""
