#! /usr/bin/env python
# Last Change: Thu Sep 06 09:00 PM 2007 J

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

# vim:syntax=python

"""This is a small module to wrap basic functionalities of alsa: it uses ctypes
for the wrapping."""

__docformat__ = 'restructuredtext'

__all__ = ['asoundlib_version', 'asoundlib_version_numbers', 'card_indexes', \
        'card_name', 'card_longname']
#================
# Load alsa lib
#================
import ctypes
from ctypes import cdll, Structure, c_int, pointer, POINTER, c_uint,\
        create_string_buffer, c_char_p, sizeof, byref, string_at, c_size_t,\
        c_void_p, c_ulong, c_uint16, c_long
try:
    from ctypes import c_int64
except ImportError, e:
    print "Cannot import c_int64 from ctypes: if you are on ubuntu/debian," +\
        " this is likely because ctypes was compiled with libffi. see" +\
        " https://launchpad.net/ubuntu/+source/python2.5/+bug/71914"
    raise e

from numpy.ctypeslib import ndpointer
CTYPES_MAJOR    = int(ctypes.__version__.split('.')[0])
CTYPES_MINOR    = int(ctypes.__version__.split('.')[1])
CTYPES_MICRO    = int(ctypes.__version__.split('.')[2])
if CTYPES_MAJOR < 1 or (CTYPES_MINOR == 0 and CTYPES_MICRO < 1):
    raise ImportError("version of ctypes is %s, expected at least %s" \
            % (ctypes.__version__, '1.0.1'))
import numpy as N

ALSALOC = 'libasound.so.2'
_ALSA = cdll.LoadLibrary(ALSALOC)
# XXX: alsa means linux, normally. How to locate the glibc ?
_C = cdll.LoadLibrary("libc.so.6")

# Check version
_ALSA.snd_asoundlib_version.args = []
_ALSA.snd_asoundlib_version.restype = c_char_p

def asoundlib_version():
    """Return the version of asoundlib as a string"""
    version = _ALSA.snd_asoundlib_version()
    return version

def asoundlib_version_numbers():
    """Return the version of asoundlib as a tuple(major, minor, micro)."""
    version = asoundlib_version()
    return tuple(int(i) for i in version.split('.'))

major, minor, micro = asoundlib_version_numbers()
if not (major == 1 and minor == 0):
    raise RuntimeError("Expected 1.0.x version, got %s instead" % asoundlib_version())

# Define pointers to opaque structures
class snd_pcm_t(Structure):
    pass

class snd_pcm_hw_params_t(Structure):
    pass

class snd_pcm_sw_params_t(Structure):
    pass

class snd_output_t(Structure):
    pass

snd_pcm_t_p = POINTER(snd_pcm_t)
snd_pcm_hw_params_t_p = POINTER(snd_pcm_hw_params_t)
snd_pcm_sw_params_t_p = POINTER(snd_pcm_sw_params_t)
snd_output_t_p = POINTER(snd_output_t)

#------------
# Define enum
#------------
SND_PCM_STREAM = {'SND_PCM_STREAM_PLAYBACK' : 0,
        'SND_PCM_STREAM_CAPTURE' : 1}

#-----------------------------------------------
# Define all the function we need from asoundlib
#-----------------------------------------------
arg1    = c_int
arg2    = POINTER(c_char_p)
_ALSA.snd_card_get_name.argtypes    = [arg1, arg2]
_ALSA.snd_card_get_name.restype     = c_int

arg1    = c_int
arg2    = POINTER(c_char_p)
_ALSA.snd_card_get_longname.argtypes    = [arg1, arg2]
_ALSA.snd_card_get_longname.restype     = c_int

arg1    = POINTER(c_int)
_ALSA.snd_card_next.argtypes    = [arg1]
_ALSA.snd_card_next.restype     = c_int

arg1    = c_int
_ALSA.snd_strerror.argtypes    = [arg1]
_ALSA.snd_strerror.restype     = c_char_p

# output related functions
arg1    = POINTER(snd_output_t_p)
_ALSA.snd_output_buffer_open.argtypes = [arg1]
_ALSA.snd_output_buffer_open.restype  = c_int

arg1    = snd_output_t_p
_ALSA.snd_output_close.argtypes = [arg1]
_ALSA.snd_output_close.restype  = c_int

arg1    = snd_output_t_p
arg2    = POINTER(c_char_p)
_ALSA.snd_output_buffer_string.argtypes = [arg1, arg2]
_ALSA.snd_output_buffer_string.restype  = c_size_t

arg1    = snd_pcm_t_p
arg2    = snd_output_t_p
_ALSA.snd_pcm_dump.argtypes = [arg1, arg2]
_ALSA.snd_pcm_dump.restype  = c_int

# pcm related functions
arg1    = POINTER(POINTER(snd_pcm_t))
arg2    = c_char_p
arg3    = c_int
arg4    = c_int
_ALSA.snd_pcm_open.argtypes = [arg1, arg2, arg3, arg4]
_ALSA.snd_pcm_open.restype  = c_int

arg1    = POINTER(snd_pcm_t)
_ALSA.snd_pcm_close.argtypes = [arg1]
_ALSA.snd_pcm_close.restype  = c_int

arg1    = POINTER(snd_pcm_hw_params_t_p)
_ALSA.snd_pcm_hw_params_malloc.argtypes = [arg1]
_ALSA.snd_pcm_hw_params_malloc.restype  = c_int

arg1    = snd_pcm_hw_params_t_p
_ALSA.snd_pcm_hw_params_free.argtypes = [arg1]
_ALSA.snd_pcm_hw_params_free.restype  = c_int

arg1    = snd_pcm_t_p
arg2    = snd_pcm_hw_params_t_p
_ALSA.snd_pcm_hw_params_any.argtypes = [arg1, arg2]
_ALSA.snd_pcm_hw_params_any.restype  = c_int

arg1    = snd_pcm_t_p
arg2    = snd_pcm_hw_params_t_p
_ALSA.snd_pcm_hw_params.argtypes = [arg1, arg2]
_ALSA.snd_pcm_hw_params.restype  = c_int

arg1    = snd_pcm_t_p
arg2    = snd_pcm_hw_params_t_p
arg3    = c_int
_ALSA.snd_pcm_hw_params_set_access.argtypes = [arg1, arg2, arg3]
_ALSA.snd_pcm_hw_params_set_access.restype  = c_int

arg1    = snd_pcm_t_p
arg2    = snd_pcm_hw_params_t_p
arg3    = POINTER(c_uint)
arg4    = c_int
_ALSA.snd_pcm_hw_params_set_rate_near.argtypes = [arg1, arg2, arg3, arg4]
_ALSA.snd_pcm_hw_params_set_rate_near.restype  = c_int

arg1    = snd_pcm_t_p
arg2    = snd_pcm_hw_params_t_p
arg3    = c_uint
_ALSA.snd_pcm_hw_params_set_channels.argtypes = [arg1, arg2, arg3]
_ALSA.snd_pcm_hw_params_set_channels.restype  = c_int

arg1    = snd_pcm_t_p
arg2    = snd_pcm_hw_params_t_p
arg3    = c_int
_ALSA.snd_pcm_hw_params_set_format.argtypes = [arg1, arg2, arg3]
_ALSA.snd_pcm_hw_params_set_format.restype  = c_int

arg1    = snd_pcm_t_p
arg2    = c_int
arg3    = c_int
arg4    = c_uint
arg5    = c_uint
arg6    = c_int
arg7    = c_uint
_ALSA.snd_pcm_set_params.argtypes = [arg1, arg2, arg3, arg4, arg5, arg6, arg7]
_ALSA.snd_pcm_set_params.restype  = c_int

# write
arg1    = snd_pcm_t_p
arg2    = c_void_p
arg3    = c_ulong
_ALSA.snd_pcm_writei.argtypes = [arg1, arg2, arg3]
_ALSA.snd_pcm_writei.restype = c_ulong
#==================
# General functions
#==================
class AlsaException(Exception):
    pass
    
class OutputBuffer():
    def __init__(self):
        ohdl = snd_output_t_p()
        st = _ALSA.snd_output_buffer_open(byref(ohdl))
        if st:
            raise AlsaException("Error creating output buffer")
        self._hdl = ohdl

    def __del__(self, close_func = _ALSA.snd_output_close):
        if hasattr(self, '_hdl'):
            if not(self._hdl == 0):
                close_func(self._hdl)
                self._hdl = 0


OHDL = OutputBuffer()

#========================
# Cards related functions
#========================
def card_indexes():
    """Returns a list containing index of cards recognized by alsa."""
    cards = []
    cur = c_int(-1)
    while 1:
        st = _ALSA.snd_card_next(byref(cur))
        if st < 0:
            raise AlsaException("Could not get next card")
        if cur.value < 0:
            break
        cards.append(cur.value)
    return tuple(cards)

def card_name(index):
    """Get the name of the card corresponding to the given index."""
    sptr = c_char_p(0)
    st = _ALSA.snd_card_get_name(index, byref(sptr))
    if st < 0:
        raise AlsaException("Error while getting card name %d: alsa error "\
                            "was %s" % (index, _ALSA.snd_strerror(st)))
    cardname = string_at(sptr)
    _C.free(sptr)
    return cardname

def card_longname(index):
    """Get the long name of the card corresponding to the given index."""
    sptr = c_char_p(0)
    st = _ALSA.snd_card_get_longname(index, byref(sptr))
    if st < 0:
        raise AlsaException("Error while getting card longname %d: alsa error "\
                            "was %s" % (index, _ALSA.snd_strerror(st)))
    cardname = string_at(sptr)
    _C.free(sptr)
    return cardname

#=======================
# Pcm related functions
#=======================
class Pcm:
    def __init__(self, device = 'default'):
        self._pcmhdl = snd_pcm_t_p()
        st = _ALSA.snd_pcm_open(byref(self._pcmhdl), device, 
                                 SND_PCM_STREAM['SND_PCM_STREAM_PLAYBACK'], 0)
        if st:
            raise AlsaException("error while opening pcm %s: %d" % (device, st))

        st = _ALSA.snd_pcm_set_params(self._pcmhdl,
                                  1,
                                  3,
                                  1,
                                  48000,
                                  1,
                                  500000) 
        if st:
            raise AlsaException("error while setting params: %s" \
                                % _ALSA.snd_strerror(st))

    def __del__(self, close_func = _ALSA.snd_pcm_close):
        if hasattr(self, '_pcmhdl'):
            if not(self._pcmhdl == 0):
                close_func(self._pcmhdl)
                self._pcmhdl = 0

    def __str__(self):
        buf = c_char_p()
        msg = "Pcm device: "
        if self._pcmhdl > 0:
            msg += " Opened\n"
            # XXX error checking
            st = _ALSA.snd_pcm_dump(self._pcmhdl, OHDL._hdl)
            st = _ALSA.snd_output_buffer_string(OHDL._hdl, byref(buf))
            if st > 0:
                msg += string_at(buf)
        return msg

    def __repr__(self):
        return self.__str__()

    def writei(self):
        a = N.random.rand(1024 * 16 * 2)
        a *= 255
        a = a.astype(N.uint8)
        bufsz = c_ulong(1024 * 2)
        for i in range(128):
            a = N.random.rand(1024 * 16 * 2)
            a *= 255
            a = a.astype(N.uint8)
            st =  _ALSA.snd_pcm_writei(self._pcmhdl, 
                                 a.ctypes.data_as(POINTER(c_uint16)),  bufsz)

#class HwParams:
#    def __init__(self, pcm = Pcm(), rate = 44100):
#        self._hwparamshdl = snd_pcm_hw_params_t_p()
#        self._pcm = pcm
#
#        st = _ALSA.snd_pcm_hw_params_malloc(byref(self._hwparamshdl))
#        if st:
#            raise AlsaException("error while allocating memory for hw params")
#
#        st = _ALSA.snd_pcm_hw_params_any(pcm._pcmhdl, self._hwparamshdl)
#        if st:
#            raise AlsaException("Broken configuration for playback: "\
#                                "no configurations available: %s" % \
#                                _ALSA.snd_strerror(st))
#
#        st = _ALSA.snd_pcm_hw_params_set_access(pcm._pcmhdl, self._hwparamshdl, 0)
#        if st:
#            raise AlsaException("Broken configuration for playback: ")
#
#        self._set_samplerate(rate)
#        self._set_channels(2)
#        self._set_format(3)
#
#        st = _ALSA.snd_pcm_hw_params(pcm._pcmhdl, self._hwparamshdl)
#        if st:
#            raise AlsaException("Broken configuration for playback: ")
#
#    def _set_samplerate(self, samplerate):
#        # XXX: Check that rrate is near samplerate...
#        rrate = c_uint(samplerate)
#        st = _ALSA.snd_pcm_hw_params_set_rate_near(self._pcm._pcmhdl, self._hwparamshdl, 
#                                               byref(rrate), 0)
#        if st:
#            raise AlsaException("Broken configuration for playback: ")
#
#    def _set_channels(self, channels):
#        # XXX: Check that rrate is near samplerate...
#        ca = c_uint(channels)
#        st = _ALSA.snd_pcm_hw_params_set_channels(pcm._pcmhdl, self._hwparamshdl, ca)
#        if st:
#            raise AlsaException("Broken configuration for playback: ")
#
#    def _set_format(self, format):
#        # XXX: Check that rrate is near samplerate...
#        ca = c_int(format)
#        st = _ALSA.snd_pcm_hw_params_set_format(pcm._pcmhdl, self._hwparamshdl, ca)
#        if st:
#            raise AlsaException("Broken configuration for playback: ")
#
#    def __del__(self, close_func = _ALSA.snd_pcm_hw_params_free):
#        if hasattr(self, '_hwparamshdl'):
#            if not(self._hwparamshdl == 0):
#                close_func(self._hwparamshdl)
#                self._hwparamshdl = 0

#class AlsaPlayer:
#    def __init__(self, device = "default"):
#        pcm = _Pcm(device)
#        hw = _HwParams()
#        err = _ALSA.snd_pcm_hw_params_any(pcm.pcmhdl, hw.hwparamshdl)
#        if err:
#            raise AlsaException("

if __name__ == '__main__':
    print card_indexes()
    print [card_name(i) for i in card_indexes()]
    print [card_longname(i) for i in card_indexes()]
    print asoundlib_version()
    print asoundlib_version_numbers()
    #a = AlsaPlayer()
    pcm = Pcm("default:0")
    #hw = HwParams(pcm)
    print pcm
    pcm.writei()
