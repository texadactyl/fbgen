"""
Generate a filterbank file conditioned on a configuration file.
"""


import os
import sys
import pathlib
import time

from fbgen_config import FilterbankObject
from fbgen_utilities import logger, oops
from fbgen_writer import write_header, write_data

LOGGING_FORMAT = "%(asctime)s - %(message)s"
DATE_FORMAT = "%d-%b-%y %H:%M:%S"
SUFFIX_FILTERBANK = ".fil"


def show_help():
    """
    Show command-line help then die.
    """
    print("\nUsage:  python3  {}  CONFIGFILE  OUTPUTFILE\n\n"
          .format(sys.argv[0]))
    sys.exit(1)


def initialization():
    """
    Initialize the fbgen process:
    1. Basic diagnosis.
    2. Set up configuration object.
    3. Return to caller:
        - configuration object
        - output file path
        - opened output file object
    """

    logger("intialization: Begin")

    # Must be a main program
    if __name__ != "__main__":
        oops("Must be a main program")

    # Must be Python 3.x
    if sys.version_info[0] < 3:
        oops("Requires Python 3")

    # Exit if no configuration file nor an output file was specified
    nargs = len(sys.argv)
    if nargs != 3:
        show_help()

    # Make sure that a filterbank output file has been requested.
    out_path = sys.argv[2]
    if pathlib.Path(out_path).suffix != SUFFIX_FILTERBANK:
        oops("Output file extension must be .fil")
    try:
        out_fwobj = open(out_path, "wb")
    except Exception as err:
        oops("initialization: open({}) failed, reason: {}"
             .format(out_path, repr(err)))

    # Process configuration file; produce a Filterbank object.
    config_path = sys.argv[1]
    if not os.path.isfile(config_path):
        oops("Cannot access config file specified as {}"
             .format(config_path))
    fbobj = FilterbankObject(config_path, out_path)

    # Done
    logger("intialization: End")
    return fbobj, out_path, out_fwobj


# ----------------- Main -----------------------------------

time_1 = time.time()
FBOBJ, OUT_PATH, OUT_FWOBJ = initialization()
write_header(FBOBJ, OUT_PATH, OUT_FWOBJ)
write_data(FBOBJ, OUT_PATH, OUT_FWOBJ)
time_2 = time.time()
et = time_2 - time_1
logger("fbgen_main: End, elapsed time = {:.1f} seconds".format(et))
