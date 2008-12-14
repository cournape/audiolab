import warnings
import copy

import numpy as np

from _sndfile import Format, Sndfile, available_file_formats, available_encodings

#+++++++++++++++++
# Public exception
#+++++++++++++++++
class PyaudioException(Exception):
    pass

class InvalidFormat(PyaudioException):
    pass

class PyaudioIOError(PyaudioException, IOError):
    pass

class WrappingError(PyaudioException):
    pass

class FlacUnsupported(RuntimeError, PyaudioException):
    pass

class formatinfo:
    def __init__(self, type = 'wav', encoding = 'pcm16', endianness = 'file'):
        """Build a valid format usable by the sndfile class when opening an
        audio file for writing.

        Deprecated, use Format class instead.

        Parameters
        ----------
            type : string
                represents the major file format (wav, etc...).
            encoding : string
                represents the encoding (pcm16, etc..).
            endianness : string
                represents the endianess.

        Notes
        -----

        Valid type strings are listed by file_format_dic.keys() Valid encoding
        strings are listed by encoding_dic.keys() Valid endianness strings are
        listed by endianness_dic.keys() """
        warnings.warn("formatinfo is deprecated, please use Format instead",
                      DeprecationWarning)
        self._format = Format(type, encoding, endianness)

    def __copy__(self):
        ret = formatinfo()
        ret._format = copy.copy(self._format)
        return ret

    def __deepcopy__(self):
        return self.__copy__()

    def __repr__(self):
        return self._format.__repr__()

    def __str__(self):
        return self._format.__str__()

_COMPAT_MODES = {"read": 'r', "write": 'w', "rwrite": 'rw'}

class sndfile:
    """Main class to open, read and write audio files"""
    def __init__(self, filename, mode='read', format=None, channels=0,
                 samplerate=0):
        """Create an instance of sndfile.

        :Parameters:
            filename : string or int
                name of the file to open (string), or file descriptor (integer)
            mode : string
                'read' for read, 'write' for write, or 'rwrite' for read and
                write.
            format : formatinfo
                when opening a new file for writing, give the format to write
                in.
            channels : int
                number of channels.
            samplerate : int
                sampling rate.

        :Returns:
            sndfile: a valid sndfile object

        Notes
        -----

        format, channels and samplerate need to be given only in the write
        modes and for raw files.  """
        warnings.warn("sndfile class is deprecated, please use Sndfile instead",
                      DeprecationWarning)
        if format is not None and not isinstance(format, formatinfo):
            raise ValueError("format argument must be None or " \
                             "formatinfo instance.")
        if format is None:
            f = None
        else:
            f = format._format
        
        self._sndfile = Sndfile(filename, _COMPAT_MODES[mode], f, channels,
                                samplerate)

        # We create a formatinfo instance from a Format info
        self._format = formatinfo()
        self._format._format = self._sndfile.format

    def close(self):
        """close the file."""
        self._sndfile.close()

    def sync(self):
        """call the operating system's function to force the writing of all
        file cache buffers to disk the file.

        No effect if file is open as read"""
        self._sndfile.sync()

    def seek(self, offset, whence=0, mode='rw'):
        """similar to python seek function, taking only in account audio data.

        :Parameters:
            offset : int
                the number of frames (eg two samples for stereo files) to move
                relatively to position set by whence.
            whence : int
                only 0 (beginning), 1 (current) and 2 (end of the file) are
                valid.
            mode : string
                If set to 'rw', both read and write pointers are updated. If
                'r' is given, only read pointer is updated, if 'w', only the
                write one is (this may of course make sense only if you open
                the file in a certain mode).

        Notes
        -----

        - one only takes into accound audio data.
        - if an invalid seek is given (beyond or before the file), a
          PyaudioIOError is launched."""
        try:
            st = self._sndfile.seek(offset, whence, mode)
        except IOError, e:
            raise PyaudioIOError(str(e))
        return st

    # Functions to get informations about the file
    def get_nframes(self):
        """ Return the number of frames of the file"""
        return self._sndfile.nframes

    def get_samplerate(self):
        """ Return the samplerate in Hz of the file"""
        return self._sndfile.samplerate

    def get_channels(self):
        """ Return the number of channels of the file"""
        return self._sndfile.channels

    def get_file_format(self):
        """return user friendly file format string"""
        return self._sndfile.format.file_format

    def get_encoding(self):
        """return user friendly encoding string"""
        return self._sndfile.format.encoding

    def get_endianness(self):
        """return user friendly endianness string"""
        return self._sndfile.format.endianness

    #------------------
    # Functions to read
    #------------------
    def read_frames(self, nframes, dtype=np.float64):
        """Read nframes frames of the file.

        :Parameters:
            nframes : int
                number of frames to read.
            dtype : numpy dtype
                dtype of the returned array containing read data (see note).

        Notes
        -----

        - read_frames updates the read pointer.
        - One column is one channel (one row per channel after 0.9)
        - if float are requested when the file contains integer data, you will
          get normalized data (that is the max possible integer will be 1.0,
          and the minimal possible value -1.0).
        - if integers are requested when the file contains floating point data,
          it may give wrong results because there is an ambiguity: if the
          floating data are normalized, you can get a file with only 0 !
          Getting integer data from files encoded in normalized floating point
          is not supported (yet: sndfile supports it)."""
        return self._sndfile.read_frames(nframes, dtype)

    #-------------------
    # Functions to write
    #-------------------
    # TODO: Think about overflow vs type of input, etc...
    def write_frames(self, input, nframes = -1):
        """write data to file.

        :Parameters:
            input : ndarray
                array containing data to write.
            nframes : int
                number of frames to write.

        Notes
        -----

        - One column is one channel (one row per channel after 0.9)
        - updates the write pointer.
        - if float are given when the file contains integer data, you should
          put normalized data (that is the range [-1..1] will be written as the
          maximum range allowed by the integer bitwidth)."""
        if nframes == -1:
            if input.ndim == 1:
                nframes = input.size
            elif input.ndim == 2:
                nframes = input.shape[0]
            else:
                raise ValueError("Input has to be rank 1 (mono) or rank 2 "\
                                 "(multi-channels)")
        return self._sndfile.write_frames(input[:nframes,...])

    # Syntactic sugar
    def __repr__(self):
        return self._sndfile.__repr__()

    def __str__(self):
        return self._sndfile.__str__()

def supported_format():
    raise RuntimeError, \
          "This function is broken. Please see " \
          "scikits.audiolab.available_file_formats"

def supported_endianness():
    raise RuntimeError, \
          "This function is broken - and does not even make sense."

def supported_encoding():
    raise RuntimeError, \
          "This function is broken. Please see " \
          "scikits.audiolab.available_encodings"
