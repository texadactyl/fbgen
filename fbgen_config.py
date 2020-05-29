"""
gendata configuration object source file
"""

import os
import configparser
from astropy.time import Time
from blimpy.io.sigproc import header_keyword_types
import astropy.units as u
from astropy.coordinates import Angle
from fbgen_utilities import logger, oops

def get_config_string(arg_config, arg_section, arg_key):
    """
    get one STRING configuration parameter by key
    """
    parm_value = "?"
    try:
        parm_value = arg_config.get(arg_section, arg_key)
    except Exception as err:
        oops("get_config_string: config file key {}, reason: {}"
             .format(arg_key, repr(err)))
    logger("get_config_string: {} = {}".format(arg_key, parm_value))
    return parm_value

def get_config_int(arg_config, arg_section, arg_key):
    """
    get one INTEGER configuration parameter by key
    """
    parm_value = -1
    try:
        parm_value = arg_config.getint(arg_section, arg_key)
    except Exception as err:
        oops("get_config_int: config file key {}, reason: {}"
             .format(arg_key, repr(err)))
    logger("get_config_int: {} = {}".format(arg_key, parm_value))
    return parm_value

def get_config_float(arg_config, arg_section, arg_key):
    """
    get one FLOAT configuration parameter by key
    """
    parm_value = -1.0
    try:
        parm_value = arg_config.getfloat(arg_section, arg_key)
    except Exception as err:
        oops("get_config_float: config file key {}, reason: {}"
             .format(arg_key, repr(err)))
    logger("get_config_float: {} = {}".format(arg_key, parm_value))
    return parm_value

class FilterbankObject:
    """
    Class definition for the configuration object.
    """

    def __init__(self, arg_config_path, arg_out_path):
        """
        Get all of the configuration parameters.
        Compute other required parameters.
        Store all of the parameters inside a Filerbank object, self.fbobj.
        """
        logger("FilterbankObject: Begin")
        try:
            config = configparser.ConfigParser()
            config.read(arg_config_path)
            section = config.sections()[0]
            logger("get_config_all: config file {} was loaded"
                   .format(arg_config_path))
        except Exception as err:
            oops("get_config: Trouble loading config file {}, reason: {}"
                 .format(arg_config_path, repr(err)))

        # Hard-coded parameter values that might be configured in the future:
        try:
            nsamples = get_config_int(config, section, "nsamples")
            tstart_iso = get_config_string(config, section, "tstart_iso")
            foff = get_config_float(config, section, "foff")
            fch1 = get_config_float(config, section, "fch1")
            nchans = get_config_int(config, section, "nchans")

            self.t_begin = 0
            self.t_end = nsamples
            self.header_keywords_types = header_keyword_types
            self.filename = os.path.basename(arg_out_path)
            self.load_data = False

            whdr = dict({
                'telescope_id': 0,  # Fake
                'az_start': 0.0,  # telescope azimuth at start of scan (degrees)
                'machine_id': 0,  # Fake
                'source_name': 'fbgen',
                'data_type': 1,    # blimpy
                'nchans': nchans,
                'ibeam': 1,
                'tsamp': get_config_float(config, section, "tsamp"),
                'foff': foff,
                'src_raj': Angle("17:10:03.984", unit=u.hour),  # right ascension (J2000) of source
                'src_dej': Angle("12:10:58.8", unit=u.deg),  # declination (J2000) of source
                'tstart': Time(tstart_iso).mjd,  # start time in MJD
                'nbeams': 1,
                'fch1': fch1,
                'za_start': 0.0, # telescope zenith angle at start (degrees)
                'rawdatafile': "N/A",  # no related guppi file
                'nifs': 1,
                'nbits': get_config_int(config, section, "nbits")
            })
            self.header = whdr

            if self.header['nbits'] in {8, 16, 32}:
                pass
            else:
                oops("get_config: {} nbits must be 8, 16, or 32"
                     .format(arg_config_path))
            if foff < 0:
                self.f_begin = fch1 + nchans * foff
                self.f_end = fch1
            else:
                self.f_begin = fch1
                self.f_end = fch1 + nchans * foff
            self.signal_low = get_config_float(config, section, "signal_low")
            self.signal_high = get_config_float(config, section, "signal_high")
            self.max_noise = get_config_float(config, section, "max_noise")

        except Exception as err:
            oops("get_config: Trouble with config file {}, reason: {}"
                 .format(arg_config_path, repr(err)))
        logger("FilterbankObject: End")


if __name__ == "__main__":
    fbobj = FilterbankObject("dfg_tiny.float32.cfg", "/tmp/xx.fil")
    print("\nDump of the Filterbank object follows:")
    print(vars(fbobj))
    print("\nt_begin:\n", fbobj.t_begin)
    print("\nkeys:\n", fbobj.header.keys())
