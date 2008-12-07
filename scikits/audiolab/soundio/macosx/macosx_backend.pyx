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

cdef extern from "Python.h":
	object PyString_FromStringAndSize(char *v, int len)

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
