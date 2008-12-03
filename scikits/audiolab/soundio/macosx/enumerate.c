#include <CoreAudio/AudioHardware.h>

int main()
{
	UInt32 sz, ndevices, buffer_size;
	AudioDeviceID *devices, odevice;
     	AudioStreamBasicDescription  ostreamdesc;
	UInt32 i;
	OSStatus st;
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

	sz = sizeof(AudioDeviceID);
	st = AudioHardwareGetProperty(
		kAudioHardwarePropertyDefaultOutputDevice,
		&sz, &odevice);

	if (odevice == kAudioDeviceUnknown) {
        	fprintf(stderr, "odevice is kAudioDeviceUnknown\n");
		return 0;
	}

	sz = sizeof(ostreamdesc);
    	st = AudioDeviceGetProperty(odevice, 0, false,
			kAudioDevicePropertyStreamFormat, &sz,
			&ostreamdesc);
	if (st) {
		fprintf(stderr, "error while getting stream format\n");
		return 0;
	}

	fprintf(stderr, "hardware format...\n");
	fprintf(stderr, "%f mSampleRate\n", ostreamdesc.mSampleRate);
	fprintf(stderr, "%c%c%c%c mFormatID\n", (int)(ostreamdesc.mFormatID &
				0xff000000) >> 24, (int)(ostreamdesc.mFormatID & 0x00ff0000) >> 16,
			(int)(ostreamdesc.mFormatID & 0x0000ff00) >>  8, (int)(ostreamdesc.mFormatID &
				0x000000ff) >>  0);
	fprintf(stderr, "%5d mBytesPerPacket\n",
			(int)ostreamdesc.mBytesPerPacket);
	fprintf(stderr, "%5d mFramesPerPacket\n",
			(int)ostreamdesc.mFramesPerPacket);
	fprintf(stderr, "%5d mBytesPerFrame\n",
			(int)ostreamdesc.mBytesPerFrame);
	fprintf(stderr, "%5d mChannelsPerFrame\n",
			(int)ostreamdesc.mChannelsPerFrame);

	/*  get the buffersize that the default device uses for IO */
	sz = sizeof (UInt32) ;
	st = AudioDeviceGetProperty(odevice, 0, false,
			kAudioDevicePropertyBufferSize,
			&sz, &buffer_size);
	if (st) {
		printf ("AudioDeviceGetProperty (kAudioDevicePropertyBufferSize) failed.\n"); 
		return ;
	} ;
	fprintf(stderr, "%5d buf size\n", buffer_size);

	return 0;
}
