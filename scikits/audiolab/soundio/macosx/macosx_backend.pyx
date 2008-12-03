cimport AudioHardware
from AudioHardware cimport *
cimport stdlib

def yo():
	cdef UInt32 sz, ndevices
	cdef AudioDeviceID *devices
	cdef char *name

	AudioHardwareGetPropertyInfo(kAudioHardwarePropertyDevices, &sz, NULL)
	ndevices = sz / sizeof(AudioDeviceID)

	print "Number of detected devices:", ndevices
