#! /usr/bin/env python
# Last Change: Sat Dec 06 11:00 PM 2008 J
from os.path import join, dirname
from os import remove
from tempfile import mkstemp

from numpy.testing import *
import numpy as N

from scikits.audiolab import wavread, auread, aiffread, sdifread, flacread, \
                             oggread
from scikits.audiolab import wavwrite, auwrite, aiffwrite, sdifwrite, flacwrite, \
                             oggwrite
from scikits.audiolab import PyaudioException
from scikits.audiolab import Sndfile, Format as audio_format
from scikits.audiolab import available_file_formats

from testcommon import open_tmp_file, close_tmp_file

AVAILABLE_FORMATS = available_file_formats()

class test_audiolab(TestCase):
    def _test_read(self, func, format, filext):
        # Create a tmp audio file, write some random data into it, and check it
        # is the expected data when read from a function from the matapi.
        rfd, fd, cfilename   = open_tmp_file('pySndfiletest.' + filext)
        try:
            nbuff = 22050
            noise = 0.1 * N.random.randn(nbuff)

            # Open the copy file for writing
            b = Sndfile(cfilename, 'write', format, 1, nbuff)
            b.write_frames(noise, nbuff)
            b.close()

            # Reread the data
            b = Sndfile(cfilename, 'read')
            rcnoise = b.read_frames(nbuff)
            b.close()

            rnoise  = func(cfilename)[0]

            assert_array_equal(rnoise, rcnoise)
        finally:
            close_tmp_file(rfd, cfilename)

    def test_wavread(self):
        """ Check wavread """
        self._test_read(wavread, audio_format('wav', 'pcm16', 'file'), 'wav')

    @dec.skipif('flac' not in AVAILABLE_FORMATS,
                "Skip flacread test, FLAC not supported by your sndfile")
    def test_flacread(self):
        """ Check flacread """
        self._test_read(flacread, audio_format('flac', 'pcm16', 'file'), 'flac')

    @dec.skipif('ogg' not in AVAILABLE_FORMATS,
                "Skip oggread test, OGG not supported by your sndfile")
    def test_oggread(self):
        """ Check oggread """
        self._test_read(oggread, audio_format('ogg', 'vorbis', 'file'), 'ogg')

    def test_auread(self):
        """ Check auread """
        self._test_read(auread, audio_format('au', 'ulaw', 'file'), 'au')

    def test_aiffread(self):
        """ Check aiffread """
        self._test_read(aiffread, audio_format('aiff', 'pcm16', 'file'), 'aiff')

    def test_sdifread(self):
        """ Check sdifread (ircam format) """
        self._test_read(sdifread, audio_format('ircam', 'pcm16', 'file'), 'sdif')

    def test_bad_wavread(self):
        """ Check wavread on bad file"""
        # Create a tmp audio file with non wav format, write some random data into it,
        # and check it can not be opened by wavread
        rfd, fd, cfilename   = open_tmp_file('pysndfiletest.wav')
        try:
            nbuff   = 22050
            noise   = 0.1 * N.random.randn(nbuff)

            # Open the copy file for writing
            format  = audio_format('aiff', 'pcm16')
            b       = Sndfile(cfilename, 'write', format, 1, nbuff)

            b.write_frames(noise, nbuff)

            b.close()

            b   = Sndfile(cfilename, 'read')
            rcnoise = b.read_frames(nbuff)
            b.close()

            try:
                rnoise  = wavread(cfilename)[0]
                raise Exception("wavread on non wav file succeded, expected to fail")
            except ValueError, e:
                pass
                #print str(e) + ", as expected"

        finally:
            close_tmp_file(rfd, cfilename)

    def _test_write(self, func, format, filext):
        """ Check *write functions from matpi """
        rfd1, fd1, cfilename1  = open_tmp_file('pysndfiletest.' + filext)
        rfd2, fd2, cfilename2  = open_tmp_file('pysndfiletest.' + filext)
        try:
            nbuff   = 22050
            fs      = nbuff
            noise   = 0.1 * N.random.randn(nbuff)

            # Open the first file for writing with Sndfile
            b       = Sndfile(cfilename1, 'write', format, 1, fs)

            b.write_frames(noise, nbuff)

            b.close()

            # Write same data with wavwrite
            func(noise, cfilename2, fs)

            # Compare if both files have same hash
            f1  = open(cfilename1)
            f2  = open(cfilename2)

            import md5

            m1  = md5.new()
            m2  = md5.new()

            m1.update(f1.read())
            m2.update(f2.read())

            f1.close()
            f2.close()
            assert m1.hexdigest() == m2.hexdigest()
        finally:
            close_tmp_file(rfd1, cfilename1)
            close_tmp_file(rfd2, cfilename2)

    def test_wavwrite(self):
        """ Check wavwrite """
        self._test_write(wavwrite, audio_format('wav', 'pcm16', 'file'), 'wav')

    def test_aiffwrite(self):
        """ Check aiffwrite """
        self._test_write(aiffwrite, audio_format('aiff', 'pcm16', 'file'), 'aiff')

    def test_auwrite(self):
        """ Check wavwrite """
        self._test_write(auwrite, audio_format('au', 'ulaw', 'file'), 'au')

    def test_sdifwrite(self):
        """ Check wavwrite """
        self._test_write(sdifwrite, audio_format('ircam', 'pcm16', 'file'), 'sdif')

    @dec.skipif('flac' not in AVAILABLE_FORMATS,
                "Skip flacwrite test, FLAC not supported by your sndfile")
    def test_flacwrite(self):
        """ Check flacwrite """
        self._test_write(flacwrite, audio_format('flac', 'pcm16', 'file'), 'flac')

    @dec.skipif('ogg' not in AVAILABLE_FORMATS,
                "Skip oggwrite test, OGG not supported by your sndfile")
    def test_oggwrite(self):
        """ Check oggwrite """
        self._test_write(oggwrite, audio_format('ogg', 'vorbis', 'file'), 'ogg')

if __name__ == "__main__":
    NumpyTest().run()
