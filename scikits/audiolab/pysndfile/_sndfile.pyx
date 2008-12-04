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

    property format:
        def __get__(self):
            return self._format_str

    property encoding:
        def __get__(self):
            return self._encoding_str

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
