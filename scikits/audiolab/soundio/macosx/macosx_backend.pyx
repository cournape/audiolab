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
cimport numpy as cnp

cdef extern from "Python.h":
    object PyString_FromStringAndSize(char *v, int len)
    cdef usleep(int)
    
cdef struct SoundData:
    int remaining

def yo():
    cdef UInt32 sz, ndevices, i
    cdef AudioDeviceID *devices
    cdef char *name

    AudioHardwareGetPropertyInfo(kAudioHardwarePropertyDevices, &sz, NULL)
    ndevices = sz / sizeof(AudioDeviceID)

    devices = <AudioDeviceID*>stdlib.malloc(sizeof(AudioDeviceID) * ndevices)
    res = []
    try:
        AudioHardwareGetProperty(kAudioHardwarePropertyDevices, &sz,
                devices)

        for i in range(ndevices):
            AudioDeviceGetPropertyInfo(devices[i], 0, False,
                           kAudioDevicePropertyDeviceName, &sz,
                           NULL)
            name = <char*>stdlib.malloc(sz + 1)
            AudioDeviceGetProperty(devices[i], 0, False,
                    kAudioDevicePropertyDeviceName, &sz,
                    name)
            devicename = PyString_FromStringAndSize(name, sz+1)
            stdlib.free(name)
            res.append(devicename)

    finally:
        stdlib.free(devices)

    return res

cdef OSStatus callback(AudioDeviceID device, AudioTimeStamp* current_time,
	AudioBufferList* data_in, AudioTimeStamp* time_in,
	AudioBufferList* data_out, AudioTimeStamp* time_out,
	void* client_data):
    cdef int sz, sample_count, read_count, k
    cdef OSStatus st = 0

    sz = (data_out[0]).mBuffers[0].mDataByteSize
    print sz, (<int*>client_data)[0]

    return st

def play(cnp.ndarray input):
    cdef UInt32 sz, buffer_size
    cdef AudioDeviceID odevice
    cdef OSStatus st
    cdef AudioStreamBasicDescription ostreamdesc
    cdef SoundData data

    # Get default output device
    sz = sizeof(AudioDeviceID)
    st = AudioHardwareGetProperty(kAudioHardwarePropertyDefaultOutputDevice, &sz,
                                  &odevice)
    if st:
        raise RuntimeError("Error getting default output properties")

    # get the buffersize that the default device uses for IO
    sz = sizeof (UInt32)
    st = AudioDeviceGetProperty(odevice, 0, False,
            kAudioDevicePropertyBufferSize,
            &sz, &buffer_size)
    if st:
        raise RuntimeError("Error getting buffer size of default output")

    # Get default output stream format
    sz = sizeof(ostreamdesc)
    st = AudioDeviceGetProperty(odevice, 0, False,
        kAudioDevicePropertyStreamFormat, &sz,
        &ostreamdesc)

    print "=================="
    print "sampling rate:", ostreamdesc.mSampleRate
    print "channels:", ostreamdesc.mChannelsPerFrame

    a = (<int>(ostreamdesc.mFormatID & 0xff000000) >> 24)
    b = (<int>(ostreamdesc.mFormatID & 0x00ff0000) >> 16)
    c = (<int>(ostreamdesc.mFormatID & 0x0000ff00) >> 8)
    d = (<int>(ostreamdesc.mFormatID & 0x000000ff) >> 0)
    print "format ID: %c%c%c%c" % (a, b, c, d)

    if ostreamdesc.mFormatID != kAudioFormatLinearPCM:
        raise RuntimeError("Not linear pcm")

    done = 0
    st = AudioDeviceAddIOProc (odevice, callback, <void*>(&data))
    if st:
        raise RuntimeError("error setting callback")

    st = AudioDeviceStart (odevice, callback)
    if st:
        raise RuntimeError("error starting ")

    done = 0
    print done
    usleep(10000)
    print done
