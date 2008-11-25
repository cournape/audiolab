import scikits.audiolab as  audiolab

a       = audiolab.sndfile('test.wav', 'read')
data    = a.read_frames(1000)
a.close()
