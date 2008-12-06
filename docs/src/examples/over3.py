from scikits.audiolab import Format, Sndfile

# Use 24 bits encoding, big endian
format = Format('wav', 'pcm24', 'big')
f = Sndfile('foo.wav', 'write', format, 2, 48000)
