#! /usr/bin/env python
# Last Change: Sun Dec 14 05:00 PM 2008 J

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

import numpy as np

from _sndfile import Format, Sndfile, available_file_formats, \
                     available_encodings, sndfile_version

__all__ = []
_MATAPI_FORMAT = ['wav', 'aiff', 'au', 'sdif', 'flac', 'ogg']
for i in _MATAPI_FORMAT:
    __all__.extend(['%sread' % i, '%swrite' % i])

# writer function factory
def _writer_factory(name, format, def_fs, descr):
    """ Create a writer function with fileformat described by format, default
    sampling rate def_fs, and docstring descr."""
    def basic_writer(data, filename, fs = def_fs, enc = format.encoding):
        """Common "template" to all write functions."""
        if np.ndim(data) <= 1:
            nc      = 1
        elif np.ndim(data) == 2:
            nc      = data.shape[1]
        else:
            RuntimeError("Only rank 0, 1, and 2 arrays supported as audio data")

        uformat = Format(format.file_format, encoding=enc,
                             endianness=format.endianness)
        hdl = Sndfile(filename, 'w', uformat, nc, fs)
        try:
            hdl.write_frames(data)
        finally:
            hdl.close()
    doc = \
    """Simple writer for %(format)s audio files.

    Parameters
    ----------
    data: array
        a rank 1 (mono) or 2 (one channel per col) numpy array
    filename: str
        audio file name
    fs : scalar
        sampling rate in Hz (%(def_fs)s by default)
    enc: str
        The encoding such as 'pcm16', etc...(%(def_enc)s by default). A
        list of supported encodings can be queried through the function
        available_encodings.

    Notes
    -----
    OVERWRITES EXISTING FILE !

    Those functions are similar manner to matlab's wavwrite/auwrite and the
    likes.  For a total control over options, such as endianness, append data
    to an existing file, etc...  you should use Sndfile class instances
    instead

    See also
    --------
    available_encodings, Sndfile, Format""" \
            % {'format' : str(descr), 'def_fs': def_fs,
               'def_enc': format.encoding}
    basic_writer.__doc__    = doc
    basic_writer.__name__   = name
    return basic_writer

# template for reader functions
def _reader_factory(name, filetype, descr):
    """Factory for reader functions ala matlab."""
    def basic_reader(filename, last = None, first = 0):
        """Common "template" to all read functions."""
        hdl = Sndfile(filename, 'r')
        try:
            if not hdl.format.file_format == filetype:
                raise ValueError, "%s is not a %s file (is %s)" \
                      % (filename, filetype, hdl.format.file_format)

            fs = hdl.samplerate
            enc = hdl.encoding
            # Set the pointer to start position
            nf  = hdl.seek(first, 1)
            if not nf == first:
                raise IOError("Error while seeking at starting position")

            if last is None:
                nframes = hdl.nframes - first
                data    = hdl.read_frames(nframes)
            else:
                data    = hdl.read_frames(last)
        finally:
            hdl.close()

        return data, fs, enc
    doc = \
    """Simple reader for %(format)s audio files.

    Parameters
    ----------
    filename : str
        Name of the file to read
    last : int
        Last frame to read. If None, this is equal to the number of frames in
        the file.
    first : int
        First frame to read. If 0, means starting from the beginning of the
        file.

    Returns
    -------
    data : array
        the read data (one column per channel)
    fs : int
        the sampling rate
    enc : str
        the encoding of the file, such as 'pcm16', 'float32', etc...

    Notes
    -----
    For a total control over options, such as output's dtype, etc...,
    you should use Sndfile class instances instead""" % {'format': str(descr)}
    basic_reader.__doc__    = doc
    basic_reader.__name__   = name
    return basic_reader

wavread     = _reader_factory('wavread', 'wav',
                    Format('wav', 'pcm16').file_format)
auread      = _reader_factory('auread', 'au',
                    Format('au', 'pcm16').file_format)
aiffread    = _reader_factory('aiffread', 'aiff',
                    Format('aiff', 'pcm16').file_format)
sdifread    = _reader_factory('sdifread', 'ircam',
                    Format('ircam', 'pcm16').file_format)

_f1          = Format('wav', 'pcm16')
wavwrite    = _writer_factory('wavwrite', _f1, 8000, _f1.file_format)

_f2          = Format('au', 'ulaw')
auwrite     = _writer_factory('auwrite', _f2, 8000, _f2.file_format)

_f3          = Format('aiff', 'pcm16')
aiffwrite   = _writer_factory('aiffwrite', _f3, 8000, _f3.file_format)

_f4          = Format('ircam', 'pcm16')
sdifwrite   = _writer_factory('sdifwrite', _f4, 44100, _f4.file_format)

# Deal with formats which may not be available depending on the sndfile version
# / build options
_AFORMATS = available_file_formats()
_SNDFILE_VER = sndfile_version()
def _missing_function(format):
    def foo(*args, **kw):
        raise NotImplementedError, \
              "Matlab API for %s is disabled: format %s is not supported by "\
              "your version of libsndfile (%s)" % (format, 
                                                    format,
                                                    _SNDFILE_VER)
    foo.__doc__ = "This function is not supported with your version " \
                  "of libsndfile."
    return foo

if 'flac' in _AFORMATS:
    f = Format('flac', 'pcm16')
    flacread = _reader_factory('flacread', 'flac', f.file_format)
    flacwrite = _writer_factory('flacwrite', f, 44100, f.file_format)
else:
    flacread = _missing_function('flac')
    flacwrite = _missing_function('flac')

if 'ogg' in _AFORMATS:
    f = Format('ogg', 'vorbis')
    oggread = _reader_factory('oggread', 'ogg', f.file_format)
    oggwrite = _writer_factory('oggwrite', f, 44100, f.file_format)
else:
    oggread = _missing_function('ogg vorbis')
    oggwrite = _missing_function('ogg_vorbis')
