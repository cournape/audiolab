import numpy as np
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
    cdef int _byfd
    cdef Format _format
    cdef int _mode
    cdef SF_INFO _sfinfo
    def __init__(Sndfile self, filename, mode='read', format=None,
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
            self._sfinfo.format = format.format_int()

        # XXX: check how cython behave with this kind of code
        if filename is int:
            raise ValueError("Opening by fd not supported yet.")
            self._byfd = SF_TRUE
        else:
            self.hdl = sf_open(filename, sfmode, &self._sfinfo)
            self.filename = filename
            self._byfd = SF_FALSE
        self._mode = sfmode

        if self.hdl == NULL:
            if self._byfd == SF_TRUE:
                msg = "error while opening file descriptor %d\n\t->" % self.fd
            else:
                msg = "error while opening file %s\n\t-> " % self.filename
            msg += sf_strerror(self.hdl)
            if self._byfd:
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
        if self.hdl:
            sf_close(self.hdl)
            self.hdl = NULL

    def samplerate(self):
        """ Return the samplerate (sampling frequency) of the file in Hz"""
        return self._sfinfo.samplerate
    
    def channels(self):
        """ Return the number of channels of the file"""
        return self._sfinfo.channels
    
    def close(Sndfile self):
        """close the file."""
        self.__del__()

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
        #if self._byfd:
        #    repstr  += "File        : %d (opened by file descriptor)\n" % self.fd
        #else:
        #    repstr  += "File        : %s\n" % self.filename
        repstr  += ["Channels    : %d" % self._sfinfo.channels]
        repstr  += ["Sample rate : %d" % self._sfinfo.samplerate]
        #repstr  += "Frames      : %d\n" % self._sfinfo.frames
        repstr  += ["Raw Format  : %#010x" % self._format.format_int()]
        repstr  += ["File format : %s" % self.file_format()]
        repstr  += ["Encoding    : %s" % self.encoding()]
        repstr  += ["Endianness  : %s" % self.endianness()]
        #repstr  += "Sections    : %d\n" % self._sfinfo.sections
        #if self._sfinfo.seekable:
        #    seek    = 'True'
        #else:
        #    seek    = 'False'
        #repstr  += "Seekable    : %s\n" % seek
        #repstr  += "Duration    : %s\n" % self._generate_duration_str()
        return "\n".join(repstr)

    def read_frames(self, sf_count_t nframes, dtype=np.float64):
        """Read nframes frames of the file.
        
        :Parameters:
            nframes : int
                number of frames to read.
            dtype : numpy dtype
                dtype of the returned array containing read data (see note)."""
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

        return y

    cdef read_frames_double(Sndfile self, sf_count_t nframes):
        cdef cnp.ndarray[cnp.float64_t, ndim=2] ty
        cdef sf_count_t res

        # Use Fortran order to cope with interleaving
        ty = np.empty((self._sfinfo.channels, nframes), 
                      dtype=np.float64, order='F')

        res = sf_readf_double(self.hdl, <double*>ty.data, nframes)
        if not res == nframes:
            raise RuntimeError("Asked %d frames, read %d" % (nframes, res))
        return ty

    cdef read_frames_float(Sndfile self, sf_count_t nframes):
        cdef cnp.ndarray[cnp.float32_t, ndim=2] ty
        cdef sf_count_t res

        # Use Fortran order to cope with interleaving
        ty = np.empty((self._sfinfo.channels, nframes), 
                      dtype=np.float32, order='F')

        res = sf_readf_float(self.hdl, <float*>ty.data, nframes)
        if not res == nframes:
            raise RuntimeError("Asked %d frames, read %d" % (nframes, res))
        return ty

    cdef read_frames_int(Sndfile self, sf_count_t nframes):
        cdef cnp.ndarray[cnp.int32_t, ndim=2] ty
        cdef sf_count_t res

        # Use Fortran order to cope with interleaving
        ty = np.empty((self._sfinfo.channels, nframes), 
                      dtype=np.int, order='F')

        res = sf_readf_int(self.hdl, <int*>ty.data, nframes)
        if not res == nframes:
            raise RuntimeError("Asked %d frames, read %d" % (nframes, res))
        return ty

    cdef read_frames_short(Sndfile self, sf_count_t nframes):
        cdef cnp.ndarray[cnp.int16_t, ndim=2] ty
        cdef sf_count_t res

        # Use Fortran order to cope with interleaving
        ty = np.empty((self._sfinfo.channels, nframes), 
                      dtype=np.short, order='F')

        res = sf_readf_short(self.hdl, <short*>ty.data, nframes)
        if not res == nframes:
            raise RuntimeError("Asked %d frames, read %d" % (nframes, res))
        return ty

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
