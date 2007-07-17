#! /usr/bin/env python
# Last Change: Tue Jul 17 11:00 AM 2007 J

from info import __doc__, __version__

from pysndfile import formatinfo, sndfile
from pysndfile import supported_format, supported_endianness, supported_encoding
from matapi import wavread, wavwrite

#__all__ = filter(lambda s:not s.startswith('_'),dir())

from numpy.testing import NumpyTest
test = NumpyTest().test

