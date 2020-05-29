"""
fbgen data writer functions
"""
import sys
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

def generate_freqs_hz(arg_fbegin, arg_fcount, arg_foff):
    """
    Based on the channel indices, construct a frequency array
    and return it to caller.  Units are Hz, not MHz.

    if the frequency interval (foff) is negative,
    then a decreasing value order is used;
    else an increasing value order is used.
    """
    ix_vals = np.arange(0, arg_fcount)
    freqs = arg_foff * ix_vals + arg_fbegin
    if DEBUGGING:
        len_freqs = len(freqs)
        print("DEBUG generate_freqs_hz len, freqs:", len_freqs, freqs)
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
    foff = arg_fbobj.header["foff"]
    len_all_freqs = arg_fbobj.header['nchans']
    n_bytes = floor(arg_fbobj.header['nbits'] / 8)
    max_freq_write = arg_fbobj.max_freq_write
    logger("write_data: #samples = {}, #freqs = {}, low = {:e}, high = {:e}"
           .format(arg_fbobj.t_end, len_all_freqs, arg_fbobj.signal_low, arg_fbobj.signal_high))
    total_chunks = floor(len_all_freqs / max_freq_write)
    modulo = len_all_freqs % max_freq_write
    if modulo > 0:
        total_chunks += 1
    logger("write_data: Frequency chunk size = {}, total chunks = {}"
           .format(max_freq_write, total_chunks))
    elapsed_time = 0.0
    for ndx_t in tqdm(range(arg_fbobj.t_begin, arg_fbobj.t_end),
                      desc="Write-progress", unit =" ticks"):

        fbegin = arg_fbobj.header["fch1"]
        fcount = max_freq_write
        nchunks = total_chunks
        if DEBUGGING:
            print("\nDEBUG before inner loop: fbegin = {}, fcount = {}, nchunks = {}"
                  .format(fbegin, fcount, nchunks))

        while nchunks > 0:
            if nchunks == 1 and modulo > 0:
                fcount = modulo
            freqs = generate_freqs_hz(fbegin, fcount, foff)
            signal = get_signal(freqs, elapsed_time,
                                arg_fbobj.signal_low, arg_fbobj.signal_high)
            rfactor = np.random.uniform(-0.5, 0.5, len(freqs))
            noisy64 = get_noisy(signal, arg_fbobj.max_noise, rfactor)
            if n_bytes == 4:
                noisy = np.float32(noisy64)
            elif n_bytes == 2:
                noisy = np.int16(noisy64)
            elif n_bytes == 1:
                noisy = np.int8(noisy64)
            else:
                oops("write_data: write({}) block #{} failed, invalid n_bytes parameter: {}"
                     .format(ndx_t, out_path, n_bytes))
            try:
                out_fwobj.write(noisy)
            except Exception as err:
                oops("write_data: write({}) block #{} failed, reason: {}"
                     .format(ndx_t, out_path, repr(err)))
            fbegin += foff * fcount
            nchunks -= 1

        elapsed_time += tsamp # end of the ndx_t loop

    print("\n")

if __name__ == "__main__":
    frequencies = np.array([101e6, 102e6, 103e6, 104e6, 105e6])
    signal_array = get_signal(frequencies, 42, 4, 8)
    print("signal:\n", signal_array)
