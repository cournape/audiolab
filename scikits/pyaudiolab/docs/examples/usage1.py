import scikits.pyaudiolab as pyaudiolab

filename    = 'test.flac'
a           = pyaudiolab.sndfile(filename, 'read')

print a
