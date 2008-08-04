import numpy as np

from _alsa import card_name, card_indexes, asoundlib_version
from _alsa import Device, AlsaException

def play(input, samplerate = 48000):
    if input.ndim == 1:
        n = input.size
        nc = 1
    elif input.ndim == 2:
        n, nc = input.shape
    else:
        raise ValueError("Only ndim 1 or 2 supported")

    if not input.dtype in (np.float32, np.float64):
        raise ValueError("input should be array of float32 or float64 !")

    try:
        dev = Device(samplerate = samplerate, channels = nc)
        dev.play_short((16384 * input).astype(np.int16))
    except AlsaException, e:
        raise IOError(str(e))

if __name__ == '__main__':
    print "Asoundlib version is", asoundlib_version()
    for i in card_indexes():
        print card_name(i)

    dev = Device()
    print "Device name:", dev.name

    a = 0.2 * np.random.randn(4e4)
    play(a, 16000)
    play(a, 8000)
    play(a, 22050)
