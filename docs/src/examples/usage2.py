import numpy as N

import scikits.audiolab as audiolab

filename    = 'test.wav'
a           = audiolab.sndfile(filename, 'read')

tmp         = a.read_frames(1e4)
float_tmp   = a.read_frames(1e4, dtype = N.float32)

import pylab as P
P.plot(tmp[:])
