#! /usr/bin/env python
# Last Change: Mon May 21 06:00 PM 2007 J
from os.path import join, dirname
from os import remove
from tempfile import mkstemp

from numpy.testing import *
import numpy as N

set_package_path()
from pyaudiolab.audiolab import wavread, auread, aiffread, sdifread, flacread
from pyaudiolab.audiolab import wavwrite, auwrite, aiffwrite, sdifwrite, flacwrite
from pyaudiolab.pysndfile import PyaudioException, sndfile, formatinfo as audio_format
from pyaudiolab.pysndfile import FlacUnsupported
restore_path()

#Optional:
set_local_path()
# import modules that are located in the same directory as this file.
restore_path()

class test_pyaudiolab(NumpyTestCase):
    def _test_read(self, func, format, filext):
        # Create a tmp wavfile, write some random data into it, 
        # and check it is the expected data
        fd, cfilename   = mkstemp('pysndfiletest.' + filext)
        try:
            nbuff   = 22050
            noise   = 0.1 * N.random.randn(nbuff)

            # Open the copy file for writing
            b       = sndfile(cfilename, 'write', format, 1, nbuff)
            b.write_frames(noise, nbuff)
            b.close()

            # Reread the data
            b   = sndfile(cfilename, 'read')
            rcnoise = b.read_frames(nbuff)
            b.close()

            rnoise  = func(cfilename)[0]

            assert_array_equal(rnoise, rcnoise)
        finally:
            remove(cfilename)

    def test_wavread(self):
        """ Check wavread """
        self._test_read(wavread, audio_format('wav', 'pcm16', 'file'), 'wav') 

    def test_flacread(self):
        """ Check flacread """
        try:
            self._test_read(flacread, audio_format('flac', 'pcm16', 'file'), 'flac') 
        except FlacUnsupported:
            print "Flac unsupported, flacread not tested"

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
        fd, cfilename   = mkstemp('pysndfiletest.wav')
        try:
            nbuff   = 22050
            noise   = 0.1 * N.random.randn(nbuff)

            # Open the copy file for writing
            format  = audio_format('aiff', 'pcm16')
            b       = sndfile(cfilename, 'write', format, 1, nbuff)

            b.write_frames(noise, nbuff)

            b.close()

            b   = sndfile(cfilename, 'read')
            rcnoise = b.read_frames(nbuff)
            b.close()

            try:
                rnoise  = wavread(cfilename)[0]
                raise Exception("wavread on non wav file succeded, expected to fail")
            except PyaudioException, e:
                print str(e) + ", as expected"

        finally:
            remove(cfilename)

    def _test_write(self, func, format, filext):
        """ Check wavwrite """
        fd, cfilename1  = mkstemp('pysndfiletest.' + filext)
        fd, cfilename2  = mkstemp('pysndfiletest.' + filext)
        try:
            nbuff   = 22050
            fs      = nbuff
            noise   = 0.1 * N.random.randn(nbuff)

            # Open the first file for writing with sndfile
            b       = sndfile(cfilename1, 'write', format, 1, fs)

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

            assert m1.hexdigest() == m2.hexdigest()
        finally:
            remove(cfilename1)
            remove(cfilename2)

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

    def test_flacwrite(self):
        """ Check flacwrite """
        try:
            self._test_write(flacwrite, audio_format('flac', 'pcm16', 'file'), 'flac')
        except FlacUnsupported:
            print "Flac unsupported, flacwrite not tested"

if __name__ == "__main__":
    NumpyTest().run()
