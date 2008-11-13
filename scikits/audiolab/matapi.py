#! /usr/bin/env python
# Last Change: Thu Nov 13 10:00 PM 2008 J

# Copyright (C) 2006-2007 Cournapeau David <cournape@gmail.com>
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
# 
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""This module implements functions to read and write to audio files easily
(ala matlab: wavread, etc...)."""

import numpy as N

from pysndfile import formatinfo, sndfile
from pysndfile import PyaudioException, FlacUnsupported

__all__ = []
_MATAPI_FORMAT = ['wav', 'aiff', 'au', 'sdif', 'flac']
for i in _MATAPI_FORMAT:
    __all__.extend(['%sread' % i, '%swrite' % i])

# writer function factory
def _writer_factory(name, format, def_fs, descr):
    """ Create a writer function with fileformat described by format, default
    sampling rate def_fs, and docstring descr."""
    def basic_writer(data, filename, fs = def_fs, enc = format.get_encoding()):
        """Common "template" to all write functions."""
        if N.ndim(data) <= 1:
            nc      = 1
            nframes = N.size(data)
        elif N.ndim(data) == 2: 
            nc      = data.shape[1]
            nframes = data.shape[0]
        else:
            RuntimeError("Only rank 0, 1, and 2 arrays supported as audio data")

        uformat = formatinfo(format.get_file_format(), encoding=enc,
                             endianness=format.get_endianness())
        hdl = sndfile(filename, 'write', uformat, nc, fs)
        try:
            hdl.write_frames(data, nframes)
        finally:
            hdl.close()
    doc = \
    """ wrapper around pysndfile to write %s file,
    in a similar manner to matlab's wavwrite/auwrite and the likes.

    OVERWRITES EXISTING FILE !

    Args:
        - data: a rank 0, 1 (mono) or 2 (one channel per col) numpy array
        - filename: a string for the audio file name 
        - fs: the sampling rate in Hz (%d Hz by default).
        - enc: a string for the encoding such as 'pcm16', etc...(%s by
          default).

    For a total control over options, such as endianness, append data to an
    existing file, etc...  you should use sndfile class instances instead""" \
            % (str(descr), def_fs, format.get_encoding())
    basic_writer.__doc__    = doc
    basic_writer.__name__   = name
    return basic_writer
    
# template for reader functions
def _reader_factory(name, filetype, descr):
    """Factory for reader functions ala matlab."""
    def basic_reader(filename, last = None, first = 0):
        """Common "template" to all read functions."""
        hdl = sndfile(filename, 'read')
        try:
            if not hdl.get_file_format() == filetype:
                raise PyaudioException("%s is not a %s file (is %s)" \
                        % (filename, filetype, hdl.get_file_format()))

            fs = hdl.get_samplerate()
            enc = hdl.get_encoding()
            # Set the pointer to start position
            nf  = hdl.seek(first, 1)
            if not nf == first:
                raise IOError("Error while seeking at starting position")

            if last is None:
                nframes = hdl.get_nframes() - first
                data    = hdl.read_frames(nframes)
            else:
                data    = hdl.read_frames(last)
        finally:
            hdl.close()

        return data, fs, enc
    doc = \
    """ wrapper around pysndfile to read a %s file in float64,
    in a similar manner to matlab wavread/auread/etc...

    Returns a tuple (data, fs, enc), where :
        - data are the read data (one column per channel)
        - fs, the sampling rate
        - enc, a string which is the encoding of the file, such as 'pcm16', 
        'float32', etc...

    For a total control over options, such as output's dtype, etc..., 
    you should use sndfile class instances instead""" % (str(descr),)
    basic_reader.__doc__    = doc
    basic_reader.__name__   = name
    return basic_reader
    
wavread     = _reader_factory('wavread', 'wav', 
                    formatinfo('wav', 'pcm16').get_major_str())
auread      = _reader_factory('auread', 'au',
                    formatinfo('au', 'pcm16').get_major_str())
aiffread    = _reader_factory('aiffread', 'aiff', 
                    formatinfo('aiff', 'pcm16').get_major_str())
sdifread    = _reader_factory('sdifread', 'ircam', 
                    formatinfo('ircam', 'pcm16').get_major_str())

_f1          = formatinfo('wav', 'pcm16')
wavwrite    = _writer_factory('wavwrite', _f1, 8000, _f1.get_major_str())

_f2          = formatinfo('au', 'ulaw')
auwrite     = _writer_factory('auwrite', _f2, 8000, _f2.get_major_str())

_f3          = formatinfo('aiff', 'pcm16')
aiffwrite   = _writer_factory('aiffwrite', _f3, 8000, _f3.get_major_str())

_f4          = formatinfo('ircam', 'pcm16')
sdifwrite   = _writer_factory('sdifwrite', _f4, 44100, _f4.get_major_str())

try:
    flacread    = _reader_factory('flacread', 'flac', 
                        formatinfo('flac', 'pcm16').get_major_str())
    _f5          = formatinfo('flac', 'pcm16')
    flacwrite   = _writer_factory('flacwrite', _f5, 44100, _f5.get_major_str())
except FlacUnsupported,e:
    print e
    print "Matlab API for FLAC is disabled"
    def missing_flacread(*args):
        raise UnimplementedError("Matlab API for FLAC is disabled on your "\
                                 "installation")
    flacread    = missing_flacread
    flacwrite   = missing_flacread
