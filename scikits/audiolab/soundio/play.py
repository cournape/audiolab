import sys
import warnings

import numpy as np

if sys.platform[:5] == 'linux':
    BACKEND = 'ALSA'
else:
    BACKEND = None

if BACKEND == 'ALSA':
    try:
        from scikits.audiolab.soundio._alsa_backend import AlsaDevice
    except ImportError, e:
        warnings.warn("Could not import alsa backend; most probably, you did not have alsa headers when building audiolab")

    def _play(input, fs):
        if input.ndim == 1:
            input = input[np.newaxis, :]
            nc = 1
        elif input.ndim == 2:
            nc = input.shape[0]
        else:
            raise ValueError, \
                  "Only input of rank 1 and 2 supported for now."

        dev = AlsaDevice(fs=fs, nchannels=nc)
        dev.play(input)
else:
    def _play(input, fs):
        raise NotImplementedError("No Backend implemented for you platform %s"
                                  % os.name)

def play(input, fs=44100):
    """Play the signal in vector input to the default output device.

    Only floating point input are supported for now: input is assumed to be in
    the -1..1 range. Any values outside this range will be clipped by the
    device.

    Parameters
    ----------
        input: array
            input signal of rank 2. Each row is assumed to be one channel.
        fs: int
            sampling rate (in Hz)
    """
    return _play(input, fs)
