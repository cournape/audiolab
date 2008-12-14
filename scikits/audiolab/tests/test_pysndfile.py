#! /usr/bin/env python
# Last Change: Sun Dec 14 07:00 PM 2008 J
"""Test for the sndfile class."""
from os.path import join, dirname
import os
import sys
import warnings

from numpy.testing import TestCase, assert_array_equal, dec
import numpy as np

from scikits.audiolab import PyaudioException, PyaudioIOError
from scikits.audiolab import sndfile, formatinfo as audio_format

from testcommon import open_tmp_file, close_tmp_file, TEST_DATA_DIR

# We filter deprecation warnings here because the features it tests will be
# deprecated themselves
warnings.filterwarnings('ignore', category=DeprecationWarning)#, module=scikits.audiolab)
# XXX: there is a lot to refactor here
class test_pysndfile(TestCase):
    def test_basic_io(self):
        """ Check open, close and basic read/write"""
        # dirty !
        ofilename = join(TEST_DATA_DIR, 'test.wav')
        rfd, fd, cfilename = open_tmp_file('pysndfiletest.wav')
        try:
            nbuff = 22050

            # Open the test file for reading
            a = sndfile(ofilename, 'read')
            nframes = a.get_nframes()

            # Open the copy file for writing
            format = audio_format('wav', 'pcm16')
            b = sndfile(fd, 'write', format, a.get_channels(),
                    a.get_samplerate())

            # Copy the data
            for i in range(nframes / nbuff):
                tmpa = a.read_frames(nbuff)
                assert tmpa.dtype == np.float
                b.write_frames(tmpa, nbuff)
            nrem = nframes % nbuff
            tmpa = a.read_frames(nrem)
            assert tmpa.dtype == np.float
            b.write_frames(tmpa, nrem)

            a.close()
            b.close()
        finally:
            close_tmp_file(rfd, cfilename)

    @dec.skipif(sys.platform=='win32', 
                "Not testing opening by fd because does not work on win32")
    def test_basic_io_fd(self):
        """ Check open from fd works"""
        ofilename = join(TEST_DATA_DIR, 'test.wav')
        fd = os.open(ofilename, os.O_RDONLY)
        hdl = sndfile(fd, 'read')
        hdl.close()

    def test_raw(self):
        rawname = join(TEST_DATA_DIR, 'test.raw')
        format = audio_format('raw', 'pcm16', 'little')
        a = sndfile(rawname, 'read', format, 1, 11025)
        assert a.get_nframes() == 11290
        a.close()

    def test_float64(self):
        """Check float64 write/read works"""
        # dirty !
        ofilename = join(TEST_DATA_DIR, 'test.wav')
        rfd, fd, cfilename = open_tmp_file('pysndfiletest.wav')
        try:
            nbuff = 22050

            # Open the test file for reading
            a = sndfile(ofilename, 'read')
            nframes = a.get_nframes()

            # Open the copy file for writing
            format = audio_format('wav', 'float64')
            b = sndfile(fd, 'write', format, a.get_channels(), 
                    a.get_samplerate())

            # Copy the data in the wav file
            for i in range(nframes / nbuff):
                tmpa = a.read_frames(nbuff, dtype = np.float64)
                assert tmpa.dtype == np.float64
                b.write_frames(tmpa, nbuff)
            nrem = nframes % nbuff
            tmpa = a.read_frames(nrem)
            b.write_frames(tmpa, nrem)

            a.close()
            b.close()

            # Now, reopen both files in for reading, and check data are
            # the same
            a = sndfile(ofilename, 'read')
            b = sndfile(cfilename, 'read')
            for i in range(nframes / nbuff):
                tmpa = a.read_frames(nbuff, dtype = np.float64)
                tmpb = b.read_frames(nbuff, dtype = np.float64)
                assert_array_equal(tmpa, tmpb)
            
            a.close()
            b.close()

        finally:
            close_tmp_file(rfd, cfilename)

    def test_float32(self):
        """Check float write/read works"""
        # dirty !
        ofilename = join(TEST_DATA_DIR, 'test.wav')
        rfd, fd, cfilename = open_tmp_file('pysndfiletest.wav')
        try:
            nbuff = 22050

            # Open the test file for reading
            a = sndfile(ofilename, 'read')
            nframes = a.get_nframes()

            # Open the copy file for writing
            format = audio_format('wav', 'float32')
            b = sndfile(fd, 'write', format, a.get_channels(), 
                    a.get_samplerate())

            # Copy the data in the wav file
            for i in range(nframes / nbuff):
                tmpa = a.read_frames(nbuff, dtype = np.float32)
                assert tmpa.dtype == np.float32
                b.write_frames(tmpa, nbuff)
            nrem = nframes % nbuff
            tmpa = a.read_frames(nrem)
            b.write_frames(tmpa, nrem)

            a.close()
            b.close()

            # Now, reopen both files in for reading, and check data are
            # the same
            a = sndfile(ofilename, 'read')
            b = sndfile(cfilename, 'read')
            for i in range(nframes / nbuff):
                tmpa = a.read_frames(nbuff, dtype = np.float32)
                tmpb = b.read_frames(nbuff, dtype = np.float32)
                assert_array_equal(tmpa, tmpb)
            
            a.close()
            b.close()

        finally:
            close_tmp_file(rfd, cfilename)

    @dec.skipif(1, "Broken test and feature")
    def test_supported_features(self):
        for i in pysndfile.supported_format():
            msg += str(i) + ', '
        print msg
        msg = "supported encoding format are : "
        for i in pysndfile.supported_encoding():
            msg += str(i) + ', '
        print msg
        msg = "supported endianness are : "
        for i in pysndfile.supported_endianness():
            msg += str(i) + ', '
        print msg

    def test_short_io(self):
        # TODO: check if neg or pos value is the highest in abs
        rfd, fd, cfilename = open_tmp_file('pysndfiletest.wav')
        try:
            nb = 2 ** 14
            nbuff = 22050
            fs = 22050
            a = np.random.random_integers(-nb, nb, nbuff)
            a = a.astype(np.short)

            # Open the file for writing
            format = audio_format('wav', 'pcm16')
            b = sndfile(fd, 'write', format, 1, fs)

            b.write_frames(a, nbuff)
            b.close()

            b = sndfile(cfilename, 'read')

            read_a = b.read_frames(nbuff, dtype = np.short)
            b.close()

            assert_array_equal(a, read_a)
            
        finally:
            close_tmp_file(rfd, cfilename)

    def test_int_io(self):
        # TODO: check if neg or pos value is the highest in abs
        rfd, fd, cfilename = open_tmp_file('pysndfiletest.wav')
        try:
            nb = 2 ** 25
            nbuff = 22050
            fs = 22050
            a = np.random.random_integers(-nb, nb, nbuff)
            a = a.astype(np.int32)

            # Open the file for writing
            format = audio_format('wav', 'pcm32')
            b = sndfile(fd, 'write', format, 1, fs)

            b.write_frames(a, nbuff)
            b.close()

            b = sndfile(cfilename, 'read')

            read_a = b.read_frames(nbuff, dtype = np.int32)
            b.close()

            assert_array_equal(a, read_a)
            
        finally:
            close_tmp_file(rfd, cfilename)

    def test_mismatch(self):
        # This test open a file for writing, but with bad args (channels and
        # nframes inverted) 
        rfd, fd, cfilename = open_tmp_file('pysndfiletest.wav')
        try:
            # Open the file for writing
            format = audio_format('wav', 'pcm16')
            try:
                b = sndfile(fd, 'write', \
                        format, channels = 22000, samplerate = 1)
                raise Exception("Try to open a file with more than 256 "\
                        "channels, this should not succeed !")
            except ValueError, e:
                #print "Gave %d channels, error detected is \"%s\"" % (22000, e)
                pass

        finally:
            close_tmp_file(rfd, cfilename)

    def test_bigframes(self):
        """ Try to seek really far"""
        rawname = join(TEST_DATA_DIR, 'test.wav')
        a = sndfile(rawname, 'read')
        try:
            try:
                a.seek(2 ** 60)
                raise Exception("Seek really succeded ! This should not happen")
            except PyaudioIOError, e:
                pass
        finally:
            a.close()

    def test_float_frames(self):
        """ Check nframes can be a float"""
        rfd, fd, cfilename = open_tmp_file('pysndfiletest.wav')
        try:
            # Open the file for writing
            format = audio_format('wav', 'pcm16')
            a = sndfile(fd, 'rwrite', format, channels = 1, 
                    samplerate = 22050)
            tmp = np.random.random_integers(-100, 100, 1000)
            tmp = tmp.astype(np.short)
            a.write_frames(tmp, tmp.size)
            a.seek(0)
            a.sync()
            ctmp = a.read_frames(1e2, dtype = np.short)
            a.close()

        finally:
            close_tmp_file(rfd, cfilename)

    def test_nofile(self):
        """ Check the failure when opening a non existing file."""
        try:
            f = sndfile("floupi.wav", "read")
            raise AssertionError("call to non existing file should not succeed")
        except IOError:
            pass
        except Exception, e:
            raise AssertionError("opening non existing file should raise a IOError exception, got %s instead" % e.__class__)

class test_seek(TestCase):
    def test_simple(self):
        ofilename = join(TEST_DATA_DIR, 'test.wav')
        # Open the test file for reading
        a = sndfile(ofilename, 'read')
        nframes = a.get_nframes()

        buffsize = 1024
        buffsize = min(nframes, buffsize)

        # First, read some frames, go back, and compare buffers
        buff = a.read_frames(buffsize)
        a.seek(0)
        buff2 = a.read_frames(buffsize)
        assert_array_equal(buff, buff2)

        a.close()

        # Now, read some frames, go back, and compare buffers
        # (check whence == 1 == SEEK_CUR)
        a = sndfile(ofilename, 'read')
        a.read_frames(buffsize)
        buff = a.read_frames(buffsize)
        a.seek(-buffsize, 1)
        buff2 = a.read_frames(buffsize)
        assert_array_equal(buff, buff2)

        a.close()

        # Now, read some frames, go back, and compare buffers
        # (check whence == 2 == SEEK_END)
        a = sndfile(ofilename, 'read')
        buff = a.read_frames(nframes)
        a.seek(-buffsize, 2)
        buff2 = a.read_frames(buffsize)
        assert_array_equal(buff[-buffsize:], buff2)

    def test_rw(self):
        """Test read/write pointers for seek."""
        ofilename = join(TEST_DATA_DIR, 'test.wav')
        rfd, fd, cfilename = open_tmp_file('rwseektest.wav')
        try:
            ref = sndfile(ofilename, 'read')
            test = sndfile(fd, 'rwrite', format = ref._format, channels =
                    ref.get_channels(), samplerate = ref.get_samplerate())
            n = 1024

            rbuff = ref.read_frames(n, dtype = np.int16)
            test.write_frames(rbuff)
            tbuff = test.read_frames(n, dtype = np.int16)

            assert_array_equal(rbuff, tbuff)

            # Test seeking both read and write pointers
            test.seek(0, 0)
            test.write_frames(rbuff)
            tbuff = test.read_frames(n, dtype = np.int16)
            assert_array_equal(rbuff, tbuff)

            # Test seeking only read pointer
            rbuff1 = rbuff.copy()
            rbuff2 = rbuff1 * 2 + 1
            rbuff2.clip(-30000, 30000)
            test.seek(0, 0, 'r')
            test.write_frames(rbuff2)
            tbuff1 = test.read_frames(n, dtype = np.int16)
            try:
                tbuff2 = test.read_frames(n, dtype = np.int16)
            except IOError, e:
                msg = "write pointer was updated in read seek !"
                msg += "\n(msg is %s)" % e
                raise AssertionError(msg) 

            assert_array_equal(rbuff1, tbuff1)
            assert_array_equal(rbuff2, tbuff2)
            if np.all(rbuff2 == tbuff1):
                raise AssertionError("write pointer was updated"\
                        " in read seek !") 

            # Test seeking only write pointer
            rbuff3 = rbuff1 * 2 - 1
            rbuff3.clip(-30000, 30000)
            test.seek(0, 0, 'rw')
            test.seek(n, 0, 'w')
            test.write_frames(rbuff3)
            tbuff1 = test.read_frames(n, np.int16)
            try:
                assert_array_equal(tbuff1, rbuff1)
            except AssertionError:
                raise AssertionError("read pointer was updated in write seek !")

            try:
                tbuff3 = test.read_frames(n, np.int16)
            except IOError, e:
                msg = "read pointer was updated in write seek !"
                msg += "\n(msg is %s)" % e
                raise AssertionError(msg) 

            assert_array_equal(tbuff3, rbuff3)
            test.close()

        finally:
            close_tmp_file(rfd, cfilename)

if __name__ == "__main__":
    NumpyTest().run()
