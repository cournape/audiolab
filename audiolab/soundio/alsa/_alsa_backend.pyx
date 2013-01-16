#
# Copyright (C) 2008 Cournapeau David <cournape@gmail.com>
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#      * Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#      * Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in
#        the documentation and/or other materials provided with the
#        distribution.
#      * Neither the author nor the names of any contributors may be used
#        to endorse or promote products derived from this software without
#        specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
#  TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import numpy as np
cimport numpy as cnp
cimport stdlib
cimport python_exc
from alsa cimport *

cdef int BUFFER_TIME  = 500000
cdef int PERIOD_TIME  = 0

cdef extern from "alsa/asoundlib.h":
        # This is needed here because it is a macro and is not recognized by
        # gccxml it seems
        int snd_pcm_hw_params_alloca(snd_pcm_hw_params_t **)
        int snd_pcm_sw_params_alloca(snd_pcm_sw_params_t **)

cdef extern from "Python.h":
        object PyString_FromStringAndSize(char *v, int len)

class AlsaException(Exception):
        pass

def alsa_version():
        """Return the version of libasound used by the alsa backend."""
        return snd_asoundlib_version()

def enumerate_devices():
        """Return list of found devices (includes user-space ones)."""
        cdef int st, card
        cdef char** hints
        cdef char* name

        devices = []
        names = []

        card = -1
        st = snd_device_name_hint(card, "pcm", <void***>&hints)
        card = 0
        while(hints[card] != NULL):
                #name = snd_device_name_get_hint(hints[card], "NAME")
                #names.append(PyString_FromStringAndSize(name, stdlib.strlen(name)))
                #if name != NULL:
                #        stdlib.free(name)
                devices.append(PyString_FromStringAndSize(hints[card], 
                        stdlib.strlen(hints[card])))
                card += 1
        snd_device_name_free_hint(<void**>hints)

        return devices

cdef struct format_info:
        # number of channels
        int nchannels
        # Rate (samples/s -> Hz)
        int rate
        # Bits per sample
        int nbits
        # Byte format
        int byte_fmt

cdef class AlsaDevice:
        cdef snd_pcm_t *handle
        cdef format_info format
        def __init__(AlsaDevice self, unsigned int fs=48000, int nchannels=1):
                cdef int st
                cdef snd_pcm_uframes_t psize, bsize

                self.format.rate = fs
                self.format.nchannels = nchannels

                if not (nchannels > 0 and nchannels < 3):
                        raise ValueError,\
                              "Only mono/stereo signals supported for now"

                self.handle = <snd_pcm_t*>0
                st = snd_pcm_open(&self.handle, "default", SND_PCM_STREAM_PLAYBACK, 0)
                if st < 0:
                        raise AlsaException("Fail opening 'default'")

                set_hw_params(self.handle, self.format, &psize, &bsize)
                print "Period size is", psize, ", Buffer size is", bsize

                set_sw_params(self.handle, psize, bsize)

        def play(AlsaDevice self, cnp.ndarray input):
                self._play(input)

        cdef int _play(AlsaDevice self, cnp.ndarray input) except -1:
                cdef cnp.ndarray[cnp.int16_t, ndim=2] tx
                cdef int nr, i, nc
                cdef int bufsize = 1024
                cdef int err = 0

                if not input.ndim == 2:
                        raise ValueError("Only rank 2 for now")

                nc = input.shape[0]
                if not nc == self.format.nchannels:
                        raise ValueError(
                              "AlsaDevice configured for %d channels, "\
                              "signal has %d channels" % (self.format.nchannels, nc))

                tx = np.empty((nc, bufsize), dtype=np.int16)
                nr = input.size / nc / bufsize

                st = snd_pcm_prepare(self.handle)
                if st:
                        raise AlsaException("Error while preparing the pcm device")

                for i in range(nr):
                        err = python_exc.PyErr_CheckSignals()
                        if err != 0:
                                break
                        # We make sure the buffer is in fortran order to deal
                        # with interleaved data.
                        tx = np.asfortranarray(
                                32568 * input[:, i * bufsize:
                                                 i * bufsize + bufsize],
                                np.int16)
                        st = snd_pcm_writei(self.handle, <void*>tx.data, bufsize)
                        if st < 0:
                                raise AlsaException("Error in writei")

                if err:
                        print "Got SIGINT: draining the pcm device... "
                        snd_pcm_drain(self.handle)
                        return -1
                snd_pcm_drain(self.handle)
                return 0

        def __dealloc__(AlsaDevice self):
                if self.handle:
                        snd_pcm_close(self.handle)

cdef set_hw_params(snd_pcm_t *hdl, format_info info, snd_pcm_uframes_t* period_size, snd_pcm_uframes_t *buffer_size):
        cdef unsigned int nchannels, buftime, pertime, samplerate
        cdef snd_pcm_hw_params_t *params
        cdef int st, dir
        cdef snd_pcm_access_t access
        cdef snd_pcm_format_t format

        access = SND_PCM_ACCESS_RW_INTERLEAVED
        buftime = BUFFER_TIME
        pertime = PERIOD_TIME

        nchannels = info.nchannels
        samplerate = info.rate
        format = SND_PCM_FORMAT_S16_LE

        snd_pcm_hw_params_alloca(&params)
        st = snd_pcm_hw_params_any(hdl, params)
        if st < 0:
                raise AlsaException("Error in _any")

        # Restrict sampling rates to the ones supported by the hardware 
        st = snd_pcm_hw_params_set_rate_resample(hdl, params, 1)
        if st < 0:
                raise AlsaException("Error in _set_rate_resample")

        st = snd_pcm_hw_params_set_access(hdl, params, access)
        if st < 0:
                raise AlsaException("Error in _set_access")

        st = snd_pcm_hw_params_set_format(hdl, params, format)
        if st < 0:
                raise AlsaException("Error in _set_format")

        st = snd_pcm_hw_params_set_channels(hdl, params, nchannels)
        if st < 0:
                raise AlsaException("Error in _set_channels")

        dir = 0
        st = snd_pcm_hw_params_set_rate_near(hdl, params, &samplerate, &dir)
        if st < 0:
                raise AlsaException("Error in _set_rate_near")

        dir = 0
        st = snd_pcm_hw_params_set_buffer_time_near(hdl, params, &buftime, &dir)
        if st < 0:
                raise AlsaException("Error in _set_buffer_near")

        dir = 0
        st = snd_pcm_hw_params_set_period_time_near(hdl, params, &pertime, &dir)
        if st < 0:
                raise AlsaException("Error in _set_period_time_near")

        st = snd_pcm_hw_params(hdl, params)
        if st < 0:
                raise AlsaException("Error in applying hw params")

        dir = 0
        st = snd_pcm_hw_params_get_period_size(params, period_size, &dir)
        if st < 0:
                raise AlsaException("Error in get_period_sizse")

        st = snd_pcm_hw_params_get_buffer_size(params, buffer_size)
        if st < 0:
                raise AlsaException("Error in get_buffer_sizse")

cdef set_sw_params(snd_pcm_t *hdl, unsigned int period_size, unsigned int buffer_size):
        cdef snd_pcm_sw_params_t *params

        snd_pcm_sw_params_alloca(&params)

        st = snd_pcm_sw_params_current(hdl, params)
        if st < 0:
                raise AlsaException("Error in _current")

        st = snd_pcm_sw_params_set_start_threshold(hdl, params, period_size)
        if st < 0:
                raise AlsaException("Error in _set_start_threshold")

        st = snd_pcm_sw_params_set_avail_min(hdl, params, period_size)
        if st < 0:
                raise AlsaException("Error in _set_avail_min")

        st = snd_pcm_sw_params(hdl, params)
        if st < 0:
                raise AlsaException("Error in applying sw params")
