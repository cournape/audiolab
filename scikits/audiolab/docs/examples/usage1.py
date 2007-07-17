import scikits.audiolab as audiolab

filename    = 'test.flac'
a           = audiolab.sndfile(filename, 'read')

print a
