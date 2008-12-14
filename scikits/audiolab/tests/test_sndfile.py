#! /usr/bin/env python
# Last Change: Sun Dec 14 07:00 PM 2008 J
"""Test for the sndfile class."""
from os.path import join, dirname
import os
import sys

from numpy.testing import TestCase, assert_array_equal, dec
import numpy as np

from scikits.audiolab import Sndfile, Format, available_encodings, available_file_formats

from testcommon import open_tmp_file, close_tmp_file, TEST_DATA_DIR

_DTYPE_TO_ENC = {np.float64 : 'float64', np.float32: 'float32', 
                 np.int32: 'pcm32', np.int16: 'pcm16'}

# XXX: there is a lot to refactor here
class TestSndfile(TestCase):
    def test_basic_io(self):
        """ Check open, close and basic read/write"""
        # dirty !
        ofilename = join(TEST_DATA_DIR, 'test.wav')
        rfd, fd, cfilename = open_tmp_file('pysndfiletest.wav')
        try:
            nbuff = 22050

            # Open the test file for reading
            a = Sndfile(ofilename, 'r')
            nframes = a.nframes

            # Open the copy file for writing
            format = Format('wav', 'pcm16')
            b = Sndfile(fd, 'w', format, a.channels, a.samplerate)

            # Copy the data
            for i in range(nframes / nbuff):
                tmpa    = a.read_frames(nbuff)
                assert tmpa.dtype == np.float
                b.write_frames(tmpa)
            nrem    = nframes % nbuff
            tmpa    = a.read_frames(nrem)
            assert tmpa.dtype == np.float
            b.write_frames(tmpa)

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
        hdl = Sndfile(fd, 'r')
        hdl.close()

    def test_raw(self):
        rawname = join(TEST_DATA_DIR, 'test.raw')
        format = Format('raw', 'pcm16', 'little')
        a = Sndfile(rawname, 'r', format, 1, 11025)
        assert a.nframes == 11290
        a.close()

    def test_float64(self):
        """Check float64 write/read works"""
        self._test_read_write(np.float64)

    def test_float32(self):
        """Check float32 write/read works"""
        self._test_read_write(np.float32)

    def test_int32(self):
        """Check 32 bits pcm write/read works"""
        self._test_read_write(np.int32)

    def test_int16(self):
        """Check 16 bits pcm write/read works"""
        self._test_read_write(np.int16)

    def _test_read_write(self, dtype):
        # dirty !
        ofilename = join(TEST_DATA_DIR, 'test.wav')
        rfd, fd, cfilename = open_tmp_file('pysndfiletest.wav')
        try:
            nbuff = 22050

            # Open the test file for reading
            a = Sndfile(ofilename, 'r')
            nframes = a.nframes

            # Open the copy file for writing
            format = Format('wav', _DTYPE_TO_ENC[dtype])
            b = Sndfile(fd, 'w', format, a.channels, a.samplerate)

            # Copy the data in the wav file
            for i in range(nframes / nbuff):
                tmpa    = a.read_frames(nbuff, dtype=dtype)
                assert tmpa.dtype == dtype
                b.write_frames(tmpa)
            nrem = nframes % nbuff
            tmpa = a.read_frames(nrem)
            b.write_frames(tmpa)

            a.close()
            b.close()

            # Now, reopen both files in for reading, and check data are
            # the same
            a = Sndfile(ofilename, 'r')
            b = Sndfile(cfilename, 'r')
            for i in range(nframes / nbuff):
                tmpa = a.read_frames(nbuff, dtype=dtype)
                tmpb = b.read_frames(nbuff, dtype=dtype)
                assert_array_equal(tmpa, tmpb)

            a.close()
            b.close()

        finally:
            close_tmp_file(rfd, cfilename)

    #def test_supported_features(self):
    #    for i in available_file_formats():
    #        print "Available encodings for format %s are : " % i
    #        for j in available_encodings(i):
    #            print '\t%s' % j

    def test_short_io(self):
        self._test_int_io(np.short)

    def test_int32_io(self):
        self._test_int_io(np.int32)

    def _test_int_io(self, dt):
        # TODO: check if neg or pos value is the highest in abs
        rfd, fd, cfilename = open_tmp_file('pysndfiletest.wav')
        try:
            # Use almost full possible range possible for the given data-type
            nb = 2 ** (8 * np.dtype(dt).itemsize - 3)
            fs = 22050
            nbuff = fs
            a = np.random.random_integers(-nb, nb, nbuff)
            a = a.astype(dt)

            # Open the file for writing
            format = Format('wav', _DTYPE_TO_ENC[dt])
            b = Sndfile(fd, 'w', format, 1, fs)

            b.write_frames(a)
            b.close()

            b = Sndfile(cfilename, 'r')

            read_a  = b.read_frames(nbuff, dtype=dt)
            b.close()

            assert_array_equal(a, read_a)

        finally:
            close_tmp_file(rfd, cfilename)

    def test_mismatch(self):
        """Check for bad arguments."""
        # This test open a file for writing, but with bad args (channels and
        # nframes inverted)
        rfd, fd, cfilename = open_tmp_file('pysndfiletest.wav')
        try:
            # Open the file for writing
            format = Format('wav', 'pcm16')
            try:
                b = Sndfile(fd, 'w', format, channels=22000, samplerate=1)
                raise AssertionError("Try to open a file with more than 256 "\
                                     "channels, this should not succeed !")
            except ValueError, e:
                pass

        finally:
            close_tmp_file(rfd, cfilename)

    def test_bigframes(self):
        """ Try to seek really far."""
        rawname = join(TEST_DATA_DIR, 'test.wav')
        a = Sndfile(rawname, 'r')
        try:
            try:
                a.seek(2 ** 60)
                raise Exception, \
                      "Seek really succeded ! This should not happen"
            except IOError, e:
                pass
        finally:
            a.close()

    def test_float_frames(self):
        """ Check nframes can be a float"""
        rfd, fd, cfilename   = open_tmp_file('pysndfiletest.wav')
        try:
            # Open the file for writing
            format = Format('wav', 'pcm16')
            a = Sndfile(fd, 'rw', format, channels=1, samplerate=22050)
            tmp = np.random.random_integers(-100, 100, 1000)
            tmp = tmp.astype(np.short)
            a.write_frames(tmp)
            a.seek(0)
            a.sync()
            ctmp = a.read_frames(1e2, dtype=np.short)
            a.close()

        finally:
            close_tmp_file(rfd, cfilename)

    def test_nofile(self):
        """ Check the failure when opening a non existing file."""
        try:
            f = Sndfile("floupi.wav", "r")
            raise AssertionError("call to non existing file should not succeed")
        except IOError:
            pass
        except Exception, e:
            raise AssertionError("opening non existing file should raise" \
                                 " a IOError exception, got %s instead" %
                                 e.__class__)

class TestSeek(TestCase):
    def test_simple(self):
        ofilename = join(TEST_DATA_DIR, 'test.wav')
        # Open the test file for reading
        a = Sndfile(ofilename, 'r')
        nframes = a.nframes

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
        a = Sndfile(ofilename, 'r')
        a.read_frames(buffsize)
        buff = a.read_frames(buffsize)
        a.seek(-buffsize, 1)
        buff2 = a.read_frames(buffsize)
        assert_array_equal(buff, buff2)

        a.close()

        # Now, read some frames, go back, and compare buffers
        # (check whence == 2 == SEEK_END)
        a = Sndfile(ofilename, 'r')
        buff = a.read_frames(nframes)
        a.seek(-buffsize, 2)
        buff2 = a.read_frames(buffsize)
        assert_array_equal(buff[-buffsize:], buff2)

    def test_rw(self):
        """Test read/write pointers for seek."""
        ofilename = join(TEST_DATA_DIR, 'test.wav')
        rfd, fd, cfilename   = open_tmp_file('rwseektest.wav')
        try:
            ref = Sndfile(ofilename, 'r')
            test = Sndfile(fd, 'rw', format=ref.format,
                           channels=ref.channels, samplerate=ref.samplerate)
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
