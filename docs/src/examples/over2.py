import numpy as np
from scikits.audiolab import Format, Sndfile

filename = 'foo.wav'

# Create some data to save as audio data: one second of stereo white noise
data = np.random.randn(48000, 2)

# Create a Sndfile instance for writing wav files @ 48000 Hz
format = Format('wav')
f = Sndfile(filename, 'w', format, 2, 48000)

# Write the first 500 frames of the signal. Note that the write_frames method
# uses tmp's numpy dtype to determine how to write to the file; sndfile also
# converts the data on the fly if necessary
f.write_frames(data[:500])

f.close()
