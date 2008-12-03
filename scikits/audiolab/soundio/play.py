import sys

if sys.platform[:5] == 'linux':
    BACKEND = 'ALSA'
else:
    BACKEND = None

if BACKEND == 'ALSA':
    try:
        from scikits.audiolab.soundio._alsa_backend import AlsaDevice
    except ImportError, e:
        print e
        raise ImportError("Error while importing alsa backend")

    def _play(input, rate):
        nc = input.shape[0]
        dev = AlsaDevice(rate=rate, nchannels=nc)
        dev.play(input)
else:
    def _play(input, rate):
        raise NotImplementedError("No Backend implemented for you platform %s"
                                  % os.name)

def play(input, rate=44100):
    """Play the signal in vector input to the default output device.

    Only floating point input are supported for now: input is assumed to be in
    the -1..1 range. Any values outside this range will be clipped by the
    device.

    Parameters
    ----------
        input: array
            input signal of rank 2. Each row is assumed to be one channel.
        rate: int
            sampling rate (in Hz)
    """
    return _play(input, rate)
