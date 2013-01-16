import audiolab as audiolab

filename    = 'test.wav'
a           = audiolab.sndfile(filename, 'read')

print a
