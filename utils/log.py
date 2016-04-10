__author__ = 'Vincent'

import logging
import config
import time

LEVEL_OFF = 0
LEVEL_ALERT = 1
LEVEL_ERROR = 2
LEVEL_INFO = 3
LEVEL_DEBUG = 4


def convert_log_level_to_logging_level():
    if config.CONFIG_LOG_LEVEL == LEVEL_OFF:
        config.CONFIG_LOG_LEVEL_LOGGING = logging.NOTSET
    elif config.CONFIG_LOG_LEVEL == LEVEL_ALERT:
        config.CONFIG_LOG_LEVEL_LOGGING = logging.CRITICAL
    elif config.CONFIG_LOG_LEVEL == LEVEL_ERROR:
        config.CONFIG_LOG_LEVEL_LOGGING = logging.ERROR
    elif config.CONFIG_LOG_LEVEL == LEVEL_INFO:
        config.CONFIG_LOG_LEVEL_LOGGING = logging.INFO
    elif config.CONFIG_LOG_LEVEL == LEVEL_DEBUG:
        config.CONFIG_LOG_LEVEL_LOGGING = logging.DEBUG


def log(value, level):
    if config.CONFIG_LOG_LEVEL > LEVEL_OFF:
        if config.LOG_OUTPUT:
            if level == LEVEL_ALERT:
                logging.critical(value)
            elif level == LEVEL_ERROR:
                logging.error(value)
            elif level == LEVEL_INFO:
                logging.info(value)
            elif level == LEVEL_DEBUG:
                logging.debug(value)

        if config.CONSOLE_OUTPUT:
            if level <= config.CONFIG_LOG_LEVEL:
                print(time.strftime('%d/%m/%y %H:%M:%S', time.localtime()) + " " + value)
