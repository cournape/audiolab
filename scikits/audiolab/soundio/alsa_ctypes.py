#! /usr/bin/env python
# Last Change: Fri Sep 07 02:00 PM 2007 J

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
        c_void_p, c_ulong, c_uint16, c_long, c_uint8, c_int16, c_float
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

arg1    = POINTER(snd_pcm_t)
_ALSA.snd_pcm_reset.argtypes = [arg1]
_ALSA.snd_pcm_reset.restype  = c_int

arg1    = POINTER(snd_pcm_t)
_ALSA.snd_pcm_drain.argtypes = [arg1]
_ALSA.snd_pcm_drain.restype  = c_int

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
arg2    = snd_pcm_hw_params_t_p
arg3    = POINTER(c_ulong)
_ALSA.snd_pcm_hw_params_set_buffer_size_near.argtypes = [arg1, arg2, arg3]
_ALSA.snd_pcm_hw_params_set_buffer_size_near.restype  = c_int

arg1    = snd_pcm_t_p
arg2    = snd_pcm_hw_params_t_p
arg3    = POINTER(c_ulong)
arg4    = c_int
_ALSA.snd_pcm_hw_params_set_period_size_near.argtypes = [arg1, arg2, arg3, arg4]
_ALSA.snd_pcm_hw_params_set_period_size_near.restype  = c_int

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
class _HwParams:
    """Small class to assure that the hw parmas are always freed."""
    def __init__(self):
        self._hdl = snd_pcm_hw_params_t_p()
        st = _ALSA.snd_pcm_hw_params_malloc(byref(self._hdl))
        if st:
            raise AlsaException("error while creating hw params %s" \
                                % _ALSA.snd_strerror(st))

    def __del__(self, close_func = _ALSA.snd_pcm_hw_params_free):
        if hasattr(self, '_hdl'):
            if not(self._hdl == 0):
                close_func(self._hdl)
                self._hdl = 0

class Pcm:
    def __init__(self, device = 'default', samplerate = 48000, channels = 1):
        self._pcmhdl = POINTER(snd_pcm_t)()

        # Open the pcm device
        st = _ALSA.snd_pcm_open(byref(self._pcmhdl), device, 
                                 SND_PCM_STREAM['SND_PCM_STREAM_PLAYBACK'], 0)
        if st:
            raise AlsaException("error while opening pcm device %s; alsa error is %s"\
                                % (device, _ALSA.snd_strerror(st)))

        # Set hw params
        self._set_hw_params(samplerate, channels)

        # Reset the pcm device
        st = _ALSA.snd_pcm_reset(self._pcmhdl)
        if st:
            raise AlsaException("error while resetting pcm : %s" \
                                % _ALSA.snd_strerror(st))

        self.nc = channels
        self.samplerate = samplerate

    def _set_hw_params(self, samplerate, channels):
        # XXX: Parameters copied from sndfile-play.c from libsndfile. Check the
        # meaning
        alsa_period_size = c_ulong(1024)
        alsa_buffer_frames = c_ulong(alsa_period_size.value * 4)

        hw = _HwParams()
        hwhdl = hw._hdl
        st = _ALSA.snd_pcm_hw_params_any(self._pcmhdl, hwhdl)
        if st < 0:
            raise AlsaException("cannot initialize hw st: %s" \
                                % _ALSA.snd_strerror(st))

        st = _ALSA.snd_pcm_hw_params_set_access(self._pcmhdl, hwhdl, 3)
        if st < 0:
            raise AlsaException("cannot initialize hw st: %s" \
                                % _ALSA.snd_strerror(st))

        rrate = c_uint(samplerate)
        st = _ALSA.snd_pcm_hw_params_set_rate_near(self._pcmhdl, hwhdl, byref(rrate), 0)
        if st < 0:
            raise AlsaException("cannot set samplerate : %s" \
                                % _ALSA.snd_strerror(st))

        st = _ALSA.snd_pcm_hw_params_set_format(self._pcmhdl, hwhdl, 14)
        if st < 0:
            raise AlsaException("cannot set format : %s" \
                                % _ALSA.snd_strerror(st))

        st = _ALSA.snd_pcm_hw_params_set_channels(self._pcmhdl, hwhdl, channels)
        if st < 0:
            raise AlsaException("cannot set number of channels : %s" \
                                % _ALSA.snd_strerror(st))

        st = _ALSA.snd_pcm_hw_params_set_buffer_size_near(self._pcmhdl, hwhdl, 
                                                          byref(alsa_buffer_frames))
        if st < 0:
            raise AlsaException("cannot set buffer size: %s" \
                                % _ALSA.snd_strerror(st))

        st = _ALSA.snd_pcm_hw_params_set_period_size_near(self._pcmhdl, hwhdl, 
                                                          byref(alsa_period_size), 0)
        if st < 0:
            raise AlsaException("cannot set period size: %s" \
                                % _ALSA.snd_strerror(st))

        st = _ALSA.snd_pcm_hw_params(self._pcmhdl, hwhdl)
        if st < 0:
            raise AlsaException("cannot set params : %s" \
                                % _ALSA.snd_strerror(st))

    def __del__(self, close_func = _ALSA.snd_pcm_close):
        if hasattr(self, '_pcmhdl'):
            try:
                self._pcmhdl[0]
                close_func(self._pcmhdl)
                self._pcmhdl = POINTER(snd_pcm_t)()
            except ValueError:
                pass

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

    def write_float(self, data):
        bufsz = 1024 * 2
        nb = data.size / bufsz / self.nc
        for i in range(nb):
            b = a[i * bufsz: (i+1) * bufsz]
            st =  _ALSA.snd_pcm_writei(self._pcmhdl, 
                                 b.ctypes.data_as(POINTER(c_float)), bufsz)
            if not st == bufsz:
                print "Error while writing to device"
        b = a[nb * bufsz: -1]
        reframes = b.size / self.nc
        st =  _ALSA.snd_pcm_writei(self._pcmhdl, 
                             b.ctypes.data_as(POINTER(c_float)), reframes)
        if not st == reframes:
            print "Error while writing to device"

        _ALSA.snd_pcm_drain(self._pcmhdl)
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
    from scikits.audiolab import wavread
    a, fs = wavread('test.wav')[:2]
    if a.ndim > 1:
        nc = a.shape[1]
    else: 
        nc = 1
    a = a.astype(N.float32)
    pcm = Pcm("default:1", 22050, channels = nc)
    print pcm
    pcm.write_float(a)
