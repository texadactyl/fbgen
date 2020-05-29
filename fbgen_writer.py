"""
fbgen data writer functions
"""
from math import floor
import numpy as np
from tqdm import tqdm
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

def generate_freqs_hz(arg_fbobj):
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
    i_vals = np.arange(0, arg_fbobj.header['nchans'])
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
    return amplitude * np.sin(arg_freqs * arg_et) + mid

def get_noisy(arg_signal, arg_max_noise, arg_rfactor):
    """Make the signal noisy"""
    return arg_signal + (arg_signal * arg_max_noise * arg_rfactor)

def write_data(arg_fbobj, out_path, out_fwobj):
    """Write the data block for each sample. """
    tsamp = arg_fbobj.header["tsamp"]
    freqs = generate_freqs_hz(arg_fbobj)
    len_freqs = len(freqs)
    n_bytes = floor(arg_fbobj.header['nbits'] / 8)
    logger("write_data: #freqs = {}, #samples = {}, low = {:e}, high = {:e}"
           .format(len(freqs), arg_fbobj.t_end, arg_fbobj.signal_low, arg_fbobj.signal_high))
    elapsed_time = 0.0
    for ndx in tqdm(range(arg_fbobj.t_begin, arg_fbobj.t_end),
                    desc="Writing ...", unit=" (channel-blocks)"):
        signal = get_signal(freqs, elapsed_time,
                            arg_fbobj.signal_low, arg_fbobj.signal_high)
        if DEBUGGING:
            print("\nDEBUG low={}, high={}, signal:\n{}"
                  .format(arg_fbobj.signal_low, arg_fbobj.signal_high, signal))
        rfactor = np.random.uniform(-0.5, 0.5, len_freqs)
        noisy64 = get_noisy(signal, arg_fbobj.max_noise, rfactor)
        if DEBUGGING:
            print("DEBUG noisy64:", noisy64)
        if n_bytes == 4:
            noisy = np.float32(noisy64)
        elif n_bytes == 2:
            noisy = np.int16(noisy64)
        elif n_bytes == 1:
            noisy = np.int8(noisy64)
        else:
            oops("write_data: write({}) block #{} failed, invalid n_bytes parameter: {}"
                 .format(ndx, out_path, n_bytes))
        try:
            out_fwobj.write(noisy)
        except Exception as err:
            oops("write_data: write({}) block #{} failed, reason: {}"
                 .format(ndx, out_path, repr(err)))
        elapsed_time += tsamp
    print("\n")

if __name__ == "__main__":
    frequencies = np.array([101e6, 102e6, 103e6, 104e6, 105e6])
    signal_array = get_signal(frequencies, 42, 4, 8)
    print("signal:\n", signal_array)
