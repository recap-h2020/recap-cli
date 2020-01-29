import logging
import os
import sys

FORMAT = '%(asctime)s [%(name)s] [%(levelname)s]  %(message)s'

LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

log_formatter = logging.Formatter(FORMAT)
root_logger = logging.getLogger()

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
root_logger.addHandler(console_handler)
root_logger.setLevel(LOG_LEVEL)

loggers = {}


def get_logger(name: str, level: str = None) -> logging.Logger:
    if name in loggers:
        return loggers[name]

    logger = logging.getLogger(name)
    if level is not None:
        logger.setLevel(level)

    loggers[name] = logger

    return logger
