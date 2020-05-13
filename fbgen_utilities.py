"""
fbgen utility functions
"""
import sys
from time import strftime, localtime

FMT_LOGGER_TIMESTAMP = "%Y-%m-%d %H:%M:%S "


def logger(arg_string: str):
    """
    Time-stamp logger
    """
    now = strftime(FMT_LOGGER_TIMESTAMP, localtime())
    print("{} {}".format(now, arg_string), flush=True)


def oops(arg_string: str):
    """
    Report an error and exit to the O/S.
    """
    logger("*** Oops, " + arg_string)
    sys.exit(86)
