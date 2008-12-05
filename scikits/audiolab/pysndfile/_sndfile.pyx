import numpy as np
import warnings
cimport numpy as cnp
cimport stdlib
from sndfile cimport *

cdef extern from "sndfile.h":
    cdef struct SF_FORMAT_INFO:
        int format
        char *name
        char *extension
    ctypedef SF_FORMAT_INFO SF_FORMAT_INFO

cdef extern from "Python.h":
    object PyString_FromStringAndSize(char *v, int len)

# format equivalence: dic used to create internally
# the right enum values from user friendly strings
_SNDFILE_ENCODING    = {
    'pcms8' : SF_FORMAT_PCM_S8,
    'pcm16' : SF_FORMAT_PCM_16,
    'pcm24' : SF_FORMAT_PCM_24,
    'pcm32' : SF_FORMAT_PCM_32,
    'pcmu8' : SF_FORMAT_PCM_U8,

    'float32' : SF_FORMAT_FLOAT,
    'float64' : SF_FORMAT_DOUBLE,

    'ulaw'      : SF_FORMAT_ULAW,
    'alaw'      : SF_FORMAT_ALAW,
    'ima_adpcm' : SF_FORMAT_IMA_ADPCM,
    'ms_adpcm'  : SF_FORMAT_MS_ADPCM,

    'gsm610'    : SF_FORMAT_GSM610,
    'vox_adpcm' : SF_FORMAT_VOX_ADPCM,

    'g721_32'   : SF_FORMAT_G721_32,
    'g723_24'   : SF_FORMAT_G723_24,
    'g723_40'   : SF_FORMAT_G723_40,

    'dww12' : SF_FORMAT_DWVW_12,
    'dww16' : SF_FORMAT_DWVW_16,
    'dww24' : SF_FORMAT_DWVW_24,
    'dwwN'  : SF_FORMAT_DWVW_N,

    'dpcm8' : SF_FORMAT_DPCM_8,
    'dpcm16': SF_FORMAT_DPCM_16
}

_SNDFILE_FILE_FORMAT = {
    'wav'   : SF_FORMAT_WAV,
    'aiff'  : SF_FORMAT_AIFF,
    'au'    : SF_FORMAT_AU,
    'raw'   : SF_FORMAT_RAW,
    'paf'   : SF_FORMAT_PAF,
    'svx'   : SF_FORMAT_SVX,
    'nist'  : SF_FORMAT_NIST,
    'voc'   : SF_FORMAT_VOC,
    'ircam' : SF_FORMAT_IRCAM,
    'wav64' : SF_FORMAT_W64,
    'mat4'  : SF_FORMAT_MAT4,
    'mat5'  : SF_FORMAT_MAT5,
    'pvf'   : SF_FORMAT_PVF,
    'xi'    : SF_FORMAT_XI,
    'htk'   : SF_FORMAT_HTK,
    'sds'   : SF_FORMAT_SDS,
    'avr'   : SF_FORMAT_AVR,
    'wavex' : SF_FORMAT_WAVEX,
    'sd2'   : SF_FORMAT_SD2,
    'flac'  : SF_FORMAT_FLAC,
    'caf'   : SF_FORMAT_CAF
}

_SNDFILE_ENDIAN = {
    'file'      : SF_ENDIAN_FILE,
    'little'    : SF_ENDIAN_LITTLE,
    'big'       : SF_ENDIAN_BIG,
    'cpu'       : SF_ENDIAN_CPU
}

# Those following dic are used internally to get user-friendly values from
# sndfile enum
_ENUM_TO_STR_ENCODING = \
        dict([(i, j) for j, i in _SNDFILE_ENCODING.items()])
_ENUM_TO_STR_FILE_FORMAT = \
        dict([(i, j) for j, i in _SNDFILE_FILE_FORMAT.items()])
_ENUM_TO_STR_ENDIAN = \
        dict([(i, j) for j, i in _SNDFILE_ENDIAN.items()])

def sndfile_version():
    """Return version of sndfile."""
    cdef int st
    cdef char buff[128]

    st = sf_command(NULL, SFC_GET_LIB_VERSION, buff, sizeof(buff))
    if st < 1:
        raise RuntimeError("Error while getting version of libsndfile")

    ver = PyString_FromStringAndSize(buff, stdlib.strlen(buff))

    # Get major, minor and micro from version
    # Template: libsndfile-X.X.XpreX with preX being optional
    version = ver.split('-')[1]
    prerelease = 0
    major, minor, micro = [i for i in version.split('.')]
    try:
        micro = int(micro)
    except ValueError,e:
        print "micro is " + str(micro)
        micro, prerelease = micro.split('pre')

    return int(major), int(minor), int(micro), prerelease

cdef class Format:
    cdef SF_INFO _sf_info
    cdef int _format_raw_int
    cdef object _type, _encoding, _endianness
    cdef object _format_str, _encoding_str, _endian_str
    def __init__(self, type = 'wav', encoding = 'pcm16', endianness = 'file'):
        """Build a valid format usable by the sndfile class when
        opening an audio file for writing.

        :Parameters:
            type : str
                represents the major file format (wav, etc...).
            encoding : str
                represents the encoding (pcm16, etc..).
            endianness : str
                represents the endianess.
        """
        cdef int format, ctype, cencoding, cendian, st
        cdef SF_FORMAT_INFO format_info
        #
        # Notes
        # -----
        #
        # Valid type strings are listed by file_format_dic.keys() Valid encoding
        # strings are listed by encoding_dic.keys() Valid endianness strings are
        # listed by endianness_dic.keys() """

        # Keep the arguments
        self._type = type
        self._encoding = encoding
        self._endianness = endianness

        # Get the internal values which corresponds to the values libsndfile
        # can understand
        try:
            ctype = _SNDFILE_FILE_FORMAT[type]
        except KeyError, e:
            raise ValueError("file format %s not recognized" % type)

        try:
            cendian = _SNDFILE_ENDIAN[endianness]
        except KeyError, e:
            raise ValueError("endianness %s not recognized" % endianness)

        try:
            cencoding = _SNDFILE_ENCODING[encoding]
        except KeyError, e:
            raise ValueError("encoding %s not recognized" % encoding)

        format = ctype | cencoding | cendian

        # Now, we need to test if the combination of format, encoding and
        # endianness is valid. sf_format_check needs also samplerate and
        # channel information, so just give a fake samplerate and channel
        # number. Looking at sndfile.c, it looks like samplerate is never
        # actually checked, and that when channels is checked, it is only
        # checked against values different than 1 or 2, so giving a value of 1
        # to channel should be ok.
        self._sf_info.channels = 1
        self._sf_info.samplerate = 8000
        self._sf_info.format = format

        ret = sf_format_check(&self._sf_info)
        if ret is not SF_TRUE:
            raise RuntimeError("sf_format_check failed: this is more likely a"\
                               " bug in audiolab, please report it")

        # Get the sndfile string description of the format type
        format_info.format = ctype
        st = sf_command(NULL, SFC_GET_FORMAT_INFO, &format_info,
                        sizeof(format_info))
        if not st == 0:
            raise RuntimeError("Could not get format string for format "\
                    "%d, " % format_info.format + "please report this" \
                    "problem to the maintainer")

        self._format_str = PyString_FromStringAndSize(format_info.name,
                                             stdlib.strlen(format_info.name))

        # Get the sndfile string description of the encoding type
        format_info.format = cencoding
        st = sf_command(NULL, SFC_GET_FORMAT_INFO, &format_info,
                        sizeof(format_info))
        if not st == 0:
            raise RuntimeError("Could not get format string for format "\
                    "%d, " % format_info.format + "please report this" \
                    "problem to the maintainer")

        self._encoding_str = PyString_FromStringAndSize(format_info.name,
                                             stdlib.strlen(format_info.name))

        self._format_raw_int = format

    property format:
        def __get__(self):
            return self._format_str

    property encoding:
        def __get__(self):
            return self._encoding_str

    cdef int format_int(self):
        """Return the full format integer (binary OR of file format, encoding
        and endianness)."""
        return self._format_raw_int

    cdef int file_format_int(self):
        """Return the file format int."""
        return self._format_raw_int & SF_FORMAT_TYPEMASK

    cdef int encoding_int(self):
        """Return the encoding part of the format int."""
        return self._format_raw_int & SF_FORMAT_SUBMASK

    cdef int endianness_int(self):
        """Return the endianness part of the format int."""
        return self._format_raw_int & SF_FORMAT_ENDMASK

    # Syntactic sugar
    def __str__(self):
        s = ["Major Format: %s" % self._format_str]
        s += ["\tEncoding Format: %s" % self._encoding_str]
        #s += ["\tEndianness: %s" % self._endian_str]
        return "\n".join(s)

    def __repr__(self):
        return self.__str__()

def available_file_formats():
    """Return lists of available major formats."""
    return [_ENUM_TO_STR_FILE_FORMAT[i & SF_FORMAT_TYPEMASK] for i in
            _major_formats_int()]

def available_encoding(major):
    """Return lists of available encoding for the given major format."""
    if not _SNDFILE_FILE_FORMAT.has_key(major):
        raise ValueError("Unknown file format %s" % major)

    return [_ENUM_TO_STR_ENCODING[i & SF_FORMAT_SUBMASK] for i in
            _sub_formats_int(_SNDFILE_FILE_FORMAT[major])]

cdef _sub_formats_int(int format):
    """Return list of subtype formats given the major format.

    NOTE: this is the low level version: takes format as an int and returns int
    encoding"""
    cdef int st, nsub
    cdef int i
    cdef SF_FORMAT_INFO info
    cdef SF_INFO sfinfo

    st = sf_command (NULL, SFC_GET_FORMAT_SUBTYPE_COUNT, &nsub, sizeof(int))
    if st:
        raise RuntimeError("Error while calling sf_command")

    subs = []
    # Not used, but necessary to pass sfinfo to sf_format_check
    sfinfo.channels = 1
    for i in range(nsub):
        info.format = i
        sf_command (NULL, SFC_GET_FORMAT_SUBTYPE, &info, sizeof (info))
        format = (format & SF_FORMAT_TYPEMASK) | info.format

        sfinfo.format = format
        if sf_format_check(&sfinfo):
            subs.append(info.format)

    return subs

cdef _major_formats_int():
    """Return list of major format *integers*."""
    cdef int st, nmajor
    cdef int i
    cdef SF_FORMAT_INFO info

    st = sf_command (NULL, SFC_GET_FORMAT_MAJOR_COUNT, &nmajor, sizeof(int))
    if st:
        raise RuntimeError("Error while calling sf_command")

    majors = []
    for i in range(nmajor):
        info.format = i
        sf_command (NULL, SFC_GET_FORMAT_MAJOR, &info, sizeof (info))
        majors.append(info.format)

    return majors

cdef class Sndfile:
    cdef SNDFILE *hdl
    cdef object filename
    cdef int fd
    cdef Format _format
    cdef int _mode
    cdef SF_INFO _sfinfo
    def __init__(Sndfile self, filename, mode='read', Format format=None,
                 int channels=0, int samplerate=0):
        """Create an instance of sndfile.

        :Parameters:
            filename : string or int
                name of the file to open (string), or file descriptor (integer)
            mode : string
                'read' for read, 'write' for write, or 'rwrite' for read and
                write.
            format : Format
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
        cdef int sfmode
        # -1 will indicate that the file has been open from filename, not from
        # file descriptor
        self.fd = -1

        self.hdl = NULL

        # Check the mode is one of the expected values
        if mode == 'read':
            sfmode = SFM_READ
        elif mode == 'write':
            sfmode = SFM_WRITE
            if format is None:
                raise ValueError, \
                      "For write mode, you should provide"\
                      "a format argument !"
        elif mode == 'rwrite':
            sfmode  = SFM_RDWR
            if format is None:
                raise ValueError, \
                      "For write mode, you should provide"\
                      "a format argument !"
        else:
            raise ValueError("mode %s not recognized" % str(mode))

        # Fill the sfinfo struct
        self._sfinfo.frames = 0
        self._sfinfo.channels = channels
        self._sfinfo.samplerate = samplerate

        self._sfinfo.sections = 0
        self._sfinfo.seekable = SF_FALSE
        if mode == 'read' and format is None:
            self._sfinfo.format = 0
        else:
            # XXX: do this correctly, by using sf_check
            if samplerate == 0 or channels == 0:
                raise ValueError, \
                      "Bad value of samplerate (%d) or channels (%d)" % \
                      (samplerate, channels)
            self._sfinfo.format = format.format_int()
            if sf_format_check(&self._sfinfo) == SF_FALSE:
                raise ValueError("Bad format specification: check arguments.")

        # XXX: check how cython behave with this kind of code
        if isinstance(filename, int):
            self.hdl = sf_open_fd(filename, sfmode, &self._sfinfo, SF_FALSE)
            self.fd = filename
            self.filename = ""
        else:
            self.hdl = sf_open(filename, sfmode, &self._sfinfo)
            self.filename = filename
        self._mode = sfmode

        if self.hdl == NULL:
            if self.fd == -1:
                msg = "error while opening file %s\n\t-> " % self.filename
            else:
                msg = "error while opening file descriptor %d\n\t->" % self.fd
            msg += sf_strerror(self.hdl)
            if not self.fd == -1:
                msg += """
(Check that the mode argument passed to sndfile is the same than the one used
when getting the file descriptor, eg do not pass 'read' to sndfile if you
passed 'write' to the method you used to get the file descriptor. If you are on
win32, you are out of luck, because its implementation of POSIX open is
broken)"""
            raise IOError("error while opening %s\n\t->%s" % (filename, msg))

        if mode == 'read':
            type, enc, endian = int_to_format(self._sfinfo.format)
            self._format = Format(type, enc, endian)
        else:
            self._format = format

        # XXX: Handle FLAC problem

    def __dealloc__(Sndfile self):
        self._close()

    cdef _close(Sndfile self):
        if self.hdl:
            sf_close(self.hdl)
            self.hdl = NULL

    def close(Sndfile self):
        """close the file."""
        self._close()

    # Functions to get informations about the file
    #def get_nframes(self):
    #    warnings.warn("Deprecated; please use the nframes attribute instead.",
    #                  DeprecationWarning)
    #    return self.nframes

    cdef sf_count_t _get_nframes(self):
        """ Return the number of frames of the file"""
        if self._mode == SFM_READ:
            # XXX: is this reliable for any file (think pipe and co ?)
            return self._sfinfo.frames

        # In write/rwrite mode, the only reliable way to get the number of
        # frames is to use seek.
        raise NotImplementedError("Sorry, getting the current number of"
                "frames in write modes is not supported yet")

    property nframes:
        def __get__(self):
            return self._get_nframes()

    property samplerate:
        def __get__(self):
            """ Return the samplerate (sampling frequency) of the file in Hz"""
            return self._sfinfo.samplerate

    property channels:
        def __get__(self):
            """ Return the number of channels of the file"""
            return self._sfinfo.channels

    def file_format(self):
        """return user friendly file format string"""
        return _ENUM_TO_STR_FILE_FORMAT[self._format.file_format_int()]

    def encoding(Sndfile self):
        """return user friendly encoding string"""
        return _ENUM_TO_STR_ENCODING[self._format.encoding_int()]

    def endianness(Sndfile self):
        """return user friendly endianness string"""
        return _ENUM_TO_STR_ENDIAN[self._format.endianness_int()]

    def __str__(Sndfile self):
        repstr = ["----------------------------------------"]
        if not self.fd == -1:
            repstr += ["File        : %d (opened by file descriptor)" % self.fd]
        else:
            repstr += ["File        : %s" % self.filename]
        repstr  += ["Channels    : %d" % self._sfinfo.channels]
        repstr  += ["Sample rate : %d" % self._sfinfo.samplerate]
        repstr  += ["Frames      : %d" % self._sfinfo.frames]
        repstr  += ["Raw Format  : %#010x" % self._format.format_int()]
        repstr  += ["File format : %s" % self.file_format()]
        repstr  += ["Encoding    : %s" % self.encoding()]
        repstr  += ["Endianness  : %s" % self.endianness()]
        #repstr  += "Sections    : %d\n" % self._sfinfo.sections
        if self._sfinfo.seekable == SF_TRUE:
            seek    = True
        else:
            seek    = False
        repstr  += ["Seekable    : %s\n" % seek]
        #repstr  += "Duration    : %s\n" % self._generate_duration_str()
        return "\n".join(repstr)

    def read_frames(self, sf_count_t nframes, dtype=np.float64):
        """Read nframes frames of the file.

        Parameters
        ----------
            nframes : int
                number of frames to read.
            dtype : numpy dtype
                dtype of the returned array containing read data (see note).

        Note
        ----

        - One column per channel.
        - if float are requested when the file contains integer data, you will
          get normalized data (that is the max possible integer will be 1.0,
          and the minimal possible value -1.0).
        - updates the write pointer.
        - if integers are requested when the file contains floating point data,
          it may give wrong results because there is an ambiguity: if the
          floating data are normalized, you can get a file with only 0 !
          Getting integer data from files encoded in normalized floating point
          is not supported (this is an audiolab limitation: sndfile supports
          it)."""
        if nframes < 0:
            raise ValueError("number of frames has to be >= 0 (was %d)" %
                             nframes)

        # TODO: inout argument
        # XXX: rank 1 vs rank 2 for mono ?
        # XXX: endianness of dtype vs endianness of sndfile ?
        if dtype == np.float64:
            y = self.read_frames_double(nframes)
        elif dtype == np.float32:
            y = self.read_frames_float(nframes)
        elif dtype == np.int32:
            y = self.read_frames_int(nframes)
        elif dtype == np.int16:
            y = self.read_frames_short(nframes)
        else:
            RuntimeError("Sorry, dtype %s not supported" % str(dtype))

        if y.shape[1] == 1:
            return y[:, 0]
        return y

    cdef read_frames_double(Sndfile self, sf_count_t nframes):
        cdef cnp.ndarray[cnp.float64_t, ndim=2] ty
        cdef sf_count_t res

        ty = np.empty((nframes, self._sfinfo.channels),
                      dtype=np.float64, order='C')

        res = sf_readf_double(self.hdl, <double*>ty.data, nframes)
        if not res == nframes:
            raise RuntimeError("Asked %d frames, read %d" % (nframes, res))
        return ty

    cdef read_frames_float(Sndfile self, sf_count_t nframes):
        cdef cnp.ndarray[cnp.float32_t, ndim=2] ty
        cdef sf_count_t res

        # Use Fortran order to cope with interleaving
        ty = np.empty((nframes, self._sfinfo.channels),
                      dtype=np.float32, order='F')

        res = sf_readf_float(self.hdl, <float*>ty.data, nframes)
        if not res == nframes:
            raise RuntimeError("Asked %d frames, read %d" % (nframes, res))
        return ty

    cdef read_frames_int(Sndfile self, sf_count_t nframes):
        cdef cnp.ndarray[cnp.int32_t, ndim=2] ty
        cdef sf_count_t res

        # Use Fortran order to cope with interleaving
        ty = np.empty((nframes, self._sfinfo.channels),
                      dtype=np.int, order='F')

        res = sf_readf_int(self.hdl, <int*>ty.data, nframes)
        if not res == nframes:
            raise RuntimeError("Asked %d frames, read %d" % (nframes, res))
        return ty

    cdef read_frames_short(Sndfile self, sf_count_t nframes):
        cdef cnp.ndarray[cnp.int16_t, ndim=2] ty
        cdef sf_count_t res

        # Use Fortran order to cope with interleaving
        ty = np.empty((nframes, self._sfinfo.channels),
                      dtype=np.short, order='F')

        res = sf_readf_short(self.hdl, <short*>ty.data, nframes)
        if not res == nframes:
            raise RuntimeError("Asked %d frames, read %d" % (nframes, res))
        return ty

    def write_frames(self, cnp.ndarray input, sf_count_t nframes = -1):
        """write data to file.

        Parameters
        ----------
            input : ndarray
                array containing data to write.
            nframes : int
                number of frames to write.

        Notes
        -----

        - One row per channel.
        - updates the write pointer.
        - if float are given when the file contains integer data, you should
          put normalized data (that is the range [-1..1] will be written as the
          maximum range allowed by the integer bitwidth)."""
        cdef int nc

        # First, get the number of channels and frames from input
        if input.ndim == 2:
            nc = input.shape[1]
        elif input.ndim == 1:
            nc = 1
            input = input[:, None]
        else:
            raise ValueError("Expect array of rank 2, got %d" % input.ndim)

        if nframes == -1:
            nframes = np.size(input)

        # Number of channels should be the one expected
        if not nc == self._sfinfo.channels:
            raise ValueError("Expected %d channels, got %d" %
                             (self._sfinfo.channels, nc))

        input = np.require(input, requirements = 'C')

        # XXX: check for overflow ?
        if input.dtype == np.float64:
            res = self.write_frames_double(input, nframes)
        elif input.dtype == np.float32:
            res = self.write_frames_float(input, nframes)
        elif input.dtype == np.int:
            res = self.write_frames_int(input, nframes)
        elif input.dtype == np.short:
            res = self.write_frames_short(input, nframes)
        else:
            raise Exception("type of input &s not understood" % str(input.dtype))

        if not(res == nframes):
            raise IOError("write %d frames, expected to write %d"
                          % res, nframes)

    cdef sf_count_t write_frames_double(self, cnp.ndarray input,
                                        sf_count_t nframes=-1):
        cdef cnp.ndarray[cnp.float64_t, ndim=2] ty

        return sf_writef_double(self.hdl, <double*>input.data, nframes)

    cdef sf_count_t write_frames_float(self, cnp.ndarray input,
                                       sf_count_t nframes=-1):
        cdef cnp.ndarray[cnp.float32_t, ndim=2] ty

        return sf_writef_float(self.hdl, <float*>input.data, nframes)

    cdef sf_count_t write_frames_int(self, cnp.ndarray input,
                                     sf_count_t nframes=-1):
        cdef cnp.ndarray[cnp.int32_t, ndim=2] ty

        return sf_writef_int(self.hdl, <int*>input.data, nframes)

    cdef sf_count_t write_frames_short(self, cnp.ndarray input,
                                       sf_count_t nframes=-1):
        cdef cnp.ndarray[cnp.int16_t, ndim=2] ty

        return sf_writef_short(self.hdl, <short*>input.data, nframes)

    def seek(Sndfile self, sf_count_t offset, int whence=0, mode='rw'):
        """similar to python seek function, taking only in account audio data.
        
        Parameters
        ----------
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

        Returns
        -------
            offset : int
                the number of frames from the beginning of the file

        Notes
        -----
        
        - one only takes into account audio data. 
        - if an invalid seek is given (beyond or before the file), an IOError
          is launched; note that this is different from the seek method of a
          File object."""
        cdef sf_count_t st
        if mode == 'rw':
            # Update both read and write pointers
            st = sf_seek(self.hdl, offset, whence)
        elif mode == 'r':
            whence = whence | SFM_READ
            st = sf_seek(self.hdl, offset, whence)
        elif mode == 'w':
            whence = whence | SFM_WRITE
            st = sf_seek(self.hdl, offset, whence)
        else:
            raise ValueError("mode should be one of 'r', 'w' or 'rw' only")

        if st == -1:
            msg = "Error while seeking, libsndfile error is %s" \
                  % sf_strerror(self.hdl)
            raise IOError(msg)
        return st

cdef int_to_format(int format):
    """Gives a triple of strings (format, encoding, endian) given actual format
    integer, as used internally by sndfile."""
    cdef int ctype, cencoding, cendian
    ctype = format & SF_FORMAT_TYPEMASK
    cencoding = format & SF_FORMAT_SUBMASK
    cendian = format & SF_FORMAT_ENDMASK

    if not format == (ctype | cencoding | cendian):
        raise RuntimeError("Inconsistent format: this is a bug")

    return _ENUM_TO_STR_FILE_FORMAT[ctype], \
           _ENUM_TO_STR_ENCODING[cencoding], \
           _ENUM_TO_STR_ENDIAN[cendian]
