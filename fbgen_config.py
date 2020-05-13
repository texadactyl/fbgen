"""
gendata configuration object source file
"""

from math import floor
import os
import configparser
from astropy.time import Time
from blimpy.io.sigproc import header_keyword_types
from astropy import units as u
from astropy.coordinates import Angle
from fbgen_utilities import logger, oops


class FilterbankObject:
    """
    Class definition for the configuration object.
    """

    def get_config_string(self, arg_config, arg_section, arg_key):
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

    def get_config_int(self, arg_config, arg_section, arg_key):
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

    def get_config_float(self, arg_config, arg_section, arg_key):
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
            nsamples = self.get_config_int(config, section, "nsamples")
            tstart_iso = self.get_config_string(config, section, "tstart_iso")
            foff = self.get_config_float(config, section, "foff")
            fch1 = self.get_config_float(config, section, "fch1")
            nchans = self.get_config_int(config, section, "nchans")

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
                'tsamp': self.get_config_float(config, section, "tsamp"),
                'foff': foff,
                'src_raj': Angle("17:10:03.984", unit=u.hour),  # right ascension (J2000) of source
                'src_dej': Angle("12:10:58.8", unit=u.deg),  # declination (J2000) of source
                'tstart': Time(tstart_iso).mjd,  # start time in MJD
                'nbeams': 1,
                'fch1': fch1,
                'za_start': 0.0, # telescope zenith angle at start (degrees)
                'rawdatafile': "N/A",  # no related guppi file
                'nifs': 1,
                'nbits': 32
            })
            self.header = whdr

            self.file_size_bytes = 0
            self.idx_data = 0
            self.n_channels_in_file = nchans
            self.n_beams_in_file = self.header['nbeams']
            self.n_pols_in_file = 1
            self.n_bytes = floor(self.header['nbits'] / 8)
            self.d_type = 'float32'
            self.n_ints_in_file = self.t_end
            self.file_shape = (self.t_end, 1, nchans)
            if foff < 0:
                self.f_begin = fch1 + nchans * foff
                self.f_end = fch1
            else:
                self.f_begin = fch1
                self.f_end = fch1 + nchans * foff
            self.t_start = self.t_begin
            self.t_stop = self.t_end
            self.f_start = self.f_begin
            self.f_stop = self.f_end
            self.selection_shape = self.file_shape
            self.chan_start_idx = 0
            self.chan_stop_idx = nchans
            self.load_data = False
            self.freq_axis = 2
            self.time_axis = 0
            self.beam_axis = 1
            self.MAX_DATA_ARRAY_SIZE = 0
            self.large_file = True
            self.signal_low = self.get_config_float(config, section, "signal_low")
            self.signal_high = self.get_config_float(config, section, "signal_high")
            self.max_noise = self.get_config_float(config, section, "max_noise")

        except Exception as err:
            oops("get_config: Trouble with config file {}, reason: {}"
                 .format(arg_config_path, repr(err)))
        logger("FilterbankObject: End")


if __name__ == "__main__":
    fbobj = FilterbankObject("fbgen.cfg", "/tmp/xx.fil")
    print("\nDump of the Filterbank object follows:")
    print(vars(fbobj))
    print("\nt_begin:\n", fbobj.t_begin)
    print("\nkeys:\n", fbobj.header.keys())
