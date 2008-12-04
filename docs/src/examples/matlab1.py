from tempfile import mkstemp
from os.path import join, dirname
from os import remove

from scikits.audiolab import wavread, wavwrite

(tmp, fs, enc)  = wavread('test.wav')
if tmp.ndim < 2:
    nc  = 1
else:
    nc  = tmp.shape[1]

print "The file has %d frames, %d channel(s)" % (tmp.shape[0], nc)
print "FS is %f, encoding is %s" % (fs, enc)

fd, cfilename   = mkstemp('pysndfiletest.wav')
try:
    wavwrite(tmp, cfilename, fs = 16000, enc = 'pcm24')
finally:
    remove(cfilename)
