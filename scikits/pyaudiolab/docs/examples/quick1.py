import scikits.pyaudiolab as  pyaudiolab

a       = pyaudiolab.sndfile('test.flac', 'read')
data    = a.read_frames(1000)
a.close()
