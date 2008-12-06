# Use 24 bits encoding, big endian
format = Format('wav', 'pcm24', 'big')
f = Sndfile(filename, 'write', format, 2, 48000)
