#include <CoreAudio/AudioHardware.h>

int main()
{
	UInt32 sz, ndevices;
	AudioDeviceID *devices;
	UInt32 i;
	char *name;

	AudioHardwareGetPropertyInfo(kAudioHardwarePropertyDevices, &sz, NULL);
	ndevices = sz / sizeof(AudioDeviceID);

	printf("%lu devices\n", ndevices);

	devices = malloc(sizeof(*devices) * ndevices);

	AudioHardwareGetProperty(kAudioHardwarePropertyDevices, &sz, devices);

	for (i = 0; i < ndevices; ++i) {
		AudioDeviceGetPropertyInfo(devices[i], 0, false,
					   kAudioDevicePropertyDeviceName, &sz,
					   NULL);
		name = malloc(sz + 1);
		AudioDeviceGetProperty(devices[i], 0, false,
				kAudioDevicePropertyDeviceName, &sz,
				name);
		printf("%s \n", name);
		free(name);
		AudioDeviceGetPropertyInfo(devices[i], 0, false,
					   kAudioDevicePropertyDeviceManufacturer, 
				           &sz,
					   NULL);
		name = malloc(sz + 1);
		AudioDeviceGetProperty(devices[i], 0, false,
				kAudioDevicePropertyDeviceManufacturer, &sz,
				name);
		printf("%s \n", name);
		free(name);
	}


	free(devices);
	return 0;
}
