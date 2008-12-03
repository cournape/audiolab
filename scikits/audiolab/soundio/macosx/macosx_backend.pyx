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

	print "Number of detected devices:", ndevices
	devices = stdlib.malloc(sizeof(*devices) * ndevices)
	res = []
	try:
		AudioHardwareGetProperty(kAudioHardwarePropertyDevices, &sz,
				devices)

		for i in range(ndevices):
			AudioDeviceGetPropertyInfo(devices[i], 0, false,
						   kAudioDevicePropertyDeviceName, &sz,
						   NULL)
			name = malloc(sz + 1)
			AudioDeviceGetProperty(devices[i], 0, false,
					kAudioDevicePropertyDeviceName, &sz,
					name)
			devicename = PyString_FromStringAndSize(name, sz+1)
			free(name)
			res.append(devicename)

	finally:
		stdlib.free(devices)

	return devicename
