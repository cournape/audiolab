from tempfile import mkstemp
from os import remove

import numpy as N
from scikits.audiolab import formatinfo as format
import scikits.audiolab as audiolab

# Create a temp file in the system temporary dir, and always remove
# it at the end
cd, filename    = mkstemp('tmptest.wav')
try:
    fmt         = format('wav', 'pcm24')
    nchannels   = 2
    fs          = 44100

    afile =  audiolab.sndfile(filename, 'write', fmt, nchannels, fs)

    # Create a stereo white noise, with Gaussian distribution
    tmp = 0.1 * N.random.randn(1000, nchannels)

    # Write the first 500 frames of the signal
    # Note that the write_frames method uses tmp's numpy dtype to determine how
    # to write to the file; sndfile also converts the data on the fly if necessary
    afile.write_frames(tmp, 500)

    afile.close()

    # Let's check that the written file has the expected meta data
    afile = audiolab.sndfile(filename, 'read')
    assert(afile.get_samplerate() == fs)
    assert(afile.get_channels() == nchannels)
    assert(afile.get_nframes() == 500)
finally:
    remove(filename)
