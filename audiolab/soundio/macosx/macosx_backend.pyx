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

cimport AudioHardware
from AudioHardware cimport *
cimport stdlib
cimport python_exc
cimport numpy as cnp

import numpy as np

cdef extern from "Python.h":
    object PyString_FromStringAndSize(char *v, int len)
    int usleep(int)
    void printf(char*, ...)
    
cdef extern from "Python.h":
    cdef struct PyArrayObject:
        pass

cdef struct CallbackData:
    int remaining
    int nframes
    int fake_stereo
    float* idata

cdef OSStatus class_callback(AudioDeviceID device, AudioTimeStamp* current_time,
        AudioBufferList* data_in, AudioTimeStamp* time_in,
        AudioBufferList* data_out, AudioTimeStamp* time_out,
        void* client_data):
    cdef OSStatus st = 0
    cdef int sz, obuffsz, i, nframes, fake_stereo, wcount
    cdef float *data, *obuffer

    # Prevent compilation warnings
    device = device
    current_time = current_time
    data_in = data_in
    time_in = time_in
    time_out = time_out

    data = (<CallbackData*>client_data)[0].idata
    nframes = (<CallbackData*>client_data)[0].nframes
    fake_stereo = (<CallbackData*>client_data)[0].fake_stereo

    sz = (data_out[0].mBuffers)[0].mDataByteSize
    obuffsz = sz / sizeof (float) ;
    obuffer = <float*>((data_out[0].mBuffers)[0].mData)

    if nframes < obuffsz:
        wcount = nframes
        (<CallbackData*>client_data)[0].remaining = 0
    else:
        wcount = obuffsz

    if fake_stereo:
        wcount /= 2
        for i in range(wcount):
            obuffer[2 * i] = data[i]
            obuffer[2 * i + 1] = data[i]
        # Fill with 0 if output buffer biffer than remaining data to be read
        for i in range(2 * wcount, obuffsz):
            obuffer[i] = 0.0
    else:
        for i in range(wcount):
            obuffer[i] = data[i]
        # Fill with 0 if output buffer biffer than remaining data to be read
        for i in range(wcount, obuffsz):
            obuffer[i] = 0.0

    (<CallbackData*>client_data)[0].nframes -= wcount
    (<CallbackData*>client_data)[0].idata += wcount

    return st

cdef class CoreAudioDevice:
    cdef AudioDeviceID dev
    cdef AudioStreamBasicDescription format
    cdef AudioDeviceIOProc callback
    cdef int proc_set, dev_started
    cdef int nchannels

    def __init__(CoreAudioDevice self, Float64 fs=48000, int nchannels=1):
        cdef UInt32 sz, buffer_size
        cdef OSStatus st

        self.proc_set = 0
        self.dev_started = 0

        self.callback = class_callback

        # Get default output
        sz = sizeof(AudioDeviceID)
        st = AudioHardwareGetProperty(kAudioHardwarePropertyDefaultOutputDevice, &sz,
                &self.dev)
        if st:
            raise RuntimeError("Error while getting default output properties.")

        # Get default output stream format
        sz = sizeof(self.format)
        st = AudioDeviceGetProperty(self.dev, 0, False,
                kAudioDevicePropertyStreamFormat, &sz,
                &self.format)
        if st:
            raise RuntimeError("Error while getting stream format.")

        # Set sampling rate and number of channels
        self.format.mSampleRate = fs

        # CoreAudio can't do mono ? Fake stereo in that case for now
        self.nchannels = nchannels
        if nchannels == 1:
            self.format.mChannelsPerFrame = 2
        else:
            self.format.mChannelsPerFrame = nchannels

        # XXX: how to make sure we have 32 bits native float here ?
        if self.format.mFormatID != kAudioFormatLinearPCM:
            raise ValueError("Not linear pcm")

        st = AudioDeviceSetProperty(self.dev, NULL, 0, False,
                kAudioDevicePropertyStreamFormat,
                sizeof(self.format), &self.format)
        if st:
            raise RuntimeError("Error while setting stream format.")

    def play(CoreAudioDevice self, cnp.ndarray input):
        cdef int nc
        cdef cnp.ndarray[cnp.float32_t, ndim=2] cinput

        if not input.ndim == 2:
            raise ValueError("Expect rank 2 array")

        if not input.dtype == np.float64:
            raise NotImplementedError("Only float64 supported for now")

        nc = input.shape[0]
        if not nc == self.nchannels:
            raise ValueError(
                    "CoreAudioDevice configured for %d channels, "\
                    "signal has %d channels" % \
                    (self.channels, nc))

        cinput = np.asfortranarray(input, np.float32)
        self._play(cinput)

    cdef int _play(CoreAudioDevice self, cnp.ndarray input) except -1:
        cdef OSStatus st
        cdef CallbackData data
        cdef int bufsize, nframes
        cdef int gotsig = 0

        data.idata = <float*>input.data
        data.nframes = input.size / input.shape[0]
        if self.nchannels == 1:
            data.fake_stereo = 1
        else:
            data.fake_stereo = 0
        data.remaining = 1

        # Add callback, and starts the device
        st = AudioDeviceAddIOProc(self.dev, self.callback, &data)
        if st:
            raise RuntimeError("error setting callback")

        st = AudioDeviceStart (self.dev, self.callback)
        if st:
            raise RuntimeError("error starting ")

        while (data.remaining == 1):
            st = python_exc.PyErr_CheckSignals()
            if st != 0:
                    gotsig = 1
                    break
            #printf("Main: %d\n", data.nframes)
            usleep(10000)

        #if self.dev_started:
        st = AudioDeviceStop(self.dev, self.callback)
        if st:
            print "AudioDeviceStop failed"

        #if self.proc_set:
        st = AudioDeviceRemoveIOProc(self.dev, self.callback)
        if st:
            print "AudioDeviceRemoveIO failed"

        if gotsig:
            return -1

        return 0
