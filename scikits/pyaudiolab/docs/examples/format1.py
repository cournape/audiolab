from scikits.pyaudiolab import formatinfo as format

f = format('aiff', 'ulaw')
print f

f = format('ircam', 'float32')
print f
