"""
fbgen data writer functions
"""
import numpy as np
from tqdm import tqdm
from astropy.constants import c
from blimpy.io.sigproc import generate_sigproc_header
from fbgen_utilities import logger, oops

TWO_PI = 2.0 * np.pi
DEBUGGING = False

def write_header(arg_fbobj, out_path, out_fwobj):
    """ Write the header"""
    try:
        hdr = generate_sigproc_header(arg_fbobj)
        out_fwobj.write(hdr)
    except Exception as err:
        oops("write_header: write({}) failed, reason: {}"
             .format(out_path, repr(err)))

def populate_freqs_hz(arg_fbobj):
    """
    Based on the channel indices, construct a frequency array
    and return it to caller.  Units are Hz, not MHz.

    if the frequency interval (foff) is negative,
    then a decreasing value order is used i.e. f_end is the first;
    else an increasing value order is used i.e. f_begin is the first.
    """
    foff = arg_fbobj.header['foff'] * 1e6
    if foff < 0:
        first_freq = arg_fbobj.f_end * 1e6
    else:
        first_freq = arg_fbobj.f_begin * 1e6
    i_vals = np.arange(arg_fbobj.chan_start_idx, arg_fbobj.chan_stop_idx + 1)
    freqs = foff * i_vals + first_freq
    return freqs

def get_signal(arg_freqs, arg_et, arg_low, arg_high):
    """
    Build and return to caller a signal array based on
    a frequency array, elapsed time, lowest data value, and the higherst data value.

    The form of the signal is a sine wave.
    """
    amplitude = 0.5 * (arg_high - arg_low)
    mid = arg_low + amplitude
    return amplitude * np.sin((TWO_PI * arg_freqs * arg_et) / c.value) + mid

def get_noisy(arg_signal, arg_max_noise, arg_rfactor):
    """Make the signal noisy"""
    return arg_signal + (arg_signal * arg_max_noise * arg_rfactor)

def write_data(arg_fbobj, out_path, out_fwobj):
    """Write the data block for each sample. """
    tsamp = arg_fbobj.header["tsamp"]
    freqs = populate_freqs_hz(arg_fbobj)
    len_freqs = len(freqs)
    logger("write_data: #freqs = {}, #samples = {}, low = {:e}, high = {:e}"
           .format(len(freqs), arg_fbobj.t_end, arg_fbobj.signal_low, arg_fbobj.signal_high))
    et = 0.0
    for ndx in tqdm(range(arg_fbobj.t_end), desc="Writing ...", unit=" (channel-blocks)"):
        signal = get_signal(freqs, et, arg_fbobj.signal_low, arg_fbobj.signal_high)
        if DEBUGGING:
            print("\nDEBUG low={}, high={}, signal:\n{}".format(arg_fbobj.signal_low, arg_fbobj.signal_high, signal))
        rfactor = np.random.uniform(-0.5, 0.5, len_freqs)
        noisy64 = get_noisy(signal, arg_fbobj.max_noise, rfactor)
        if DEBUGGING:
            print("DEBUG noisy64:", noisy64)
        if arg_fbobj.n_bytes == 4:
            noisy = np.float32(noisy64)
        elif arg_fbobj.n_bytes == 2:
            noisy = np.int16(noisy64)
        elif arg_fbobj.n_bytes == 1:
            noisy = np.int8(noisy64)
        else:
            oops("write_data: write({}) block #{} failed, invalid n_bytes: {}"
                 .format(arg_fbobj.n_bytes))
        try:
            out_fwobj.write(noisy)
        except Exception as err:
            oops("write_data: write({}) block #{} failed, reason: {}"
                 .format(ndx, out_path, repr(err)))
        et += tsamp
    print("\n")

if __name__ == "__main__":
    freqs = np.array([101e6, 102e6, 103e6, 104e6, 105e6])
    signal = get_signal(freqs, 4, 8)
    print("signal:\n", signal)
