#! /usr/bin/env python
# Last Change: Tue Mar 24 08:00 PM 2009 J
"""
audiolab: a small toolbox to read, write and play audio to and from
numpy arrays.

audiolab provides two API:

    - one similar to matlab: this gives you wavread, wavwrite functions really
      similar to matlab's functions.
    - a more complete API, which can be used to read, write to many audio file
      (including wav, aiff, flac, au, IRCAM, htk, etc...), with IO capabilities
      not available to matlab (seek, append data, etc...)

It is a thin wrapper around libsndfile from Erik de Castro Lopo.

Copyright (C) 2006-2007 Cournapeau David <cournape@gmail.com>

LICENSE: audiolab is licensed under the LGPL, as is libsndfile itself. See
COPYING.txt for details.  """

from version import version as _version
__version__ = _version

from pysndfile import formatinfo, sndfile
from pysndfile import supported_format, supported_endianness, \
                      supported_encoding, PyaudioException, \
                      PyaudioIOError
from pysndfile import Sndfile, Format, available_file_formats, \
                      available_encodings, sndfile_version
__sndfile_version__ = ".".join([str(i) for i in sndfile_version()])
#from scikits.audiolab.matapi import wavread, aiffread, flacread, auread, \
#        sdifread, wavwrite, aiffwrite, flacwrite, auwrite, sdifwrite
from pysndfile.matapi import *

from soundio import play
__all__ = filter(lambda s:not s.startswith('_'),dir())

from numpy.testing import Tester

test = Tester().test
bench = Tester().bench
