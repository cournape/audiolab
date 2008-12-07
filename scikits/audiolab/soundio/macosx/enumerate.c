#include <CoreAudio/AudioHardware.h>

#include <stdio.h>
#include <unistd.h>

const size_t NCHANNELS = 2;
const size_t SAMPLERATE = 48000;

int enumerate_devices()
{
	UInt32 sz, ndevices, i;
	AudioDeviceID *devices;
	char *name;

	AudioHardwareGetPropertyInfo(kAudioHardwarePropertyDevices, &sz, NULL);
	ndevices = sz / sizeof(AudioDeviceID);

	printf("%lu devices\n", ndevices);

	devices = malloc(sizeof(*devices) * ndevices);

	AudioHardwareGetProperty(kAudioHardwarePropertyDevices, &sz, devices);

	for (i = 0; i < ndevices; ++i) {
		/* Get name of device */
		AudioDeviceGetPropertyInfo(devices[i], 0, false,
					   kAudioDevicePropertyDeviceName, &sz,
					   NULL);
		name = malloc(sz + 1);
		AudioDeviceGetProperty(devices[i], 0, false,
				kAudioDevicePropertyDeviceName, &sz,
				name);
		printf("%s \n", name);
		free(name);

		/* Get manufacturer of device */
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

static int prop()
{
	UInt32 sz, buffer_size;
	AudioDeviceID odevice;
	AudioStreamBasicDescription  ostreamdesc;
	OSStatus st;

	/* Get default output device */
	sz = sizeof(AudioDeviceID);
	st = AudioHardwareGetProperty(
			kAudioHardwarePropertyDefaultOutputDevice,
			&sz, &odevice);

	if (odevice == kAudioDeviceUnknown) {
		fprintf(stderr, "odevice is kAudioDeviceUnknown\n");
		return -1;
	}

	/* Get stream properties of output device */
	sz = sizeof(ostreamdesc);
	st = AudioDeviceGetProperty(odevice, 0, false,
			kAudioDevicePropertyStreamFormat, &sz,
			&ostreamdesc);
	if (st) {
		fprintf(stderr, "error while getting stream format\n");
		return -1;
	}

	fprintf(stderr, "hardware format...\n");
	fprintf(stderr, "samplerate: %f \n", ostreamdesc.mSampleRate);
	fprintf(stderr, "%c%c%c%c mFormatID\n", 
			(int)(ostreamdesc.mFormatID & 0xff000000) >> 24, 
			(int)(ostreamdesc.mFormatID & 0x00ff0000) >> 16,
			(int)(ostreamdesc.mFormatID & 0x0000ff00) >>  8, 
			(int)(ostreamdesc.mFormatID & 0x000000ff) >>  0);
	fprintf(stderr, "%5d mBytesPerPacket\n",
			(int)ostreamdesc.mBytesPerPacket);
	fprintf(stderr, "%5d mFramesPerPacket\n",
			(int)ostreamdesc.mFramesPerPacket);
	fprintf(stderr, "%5d mBytesPerFrame\n",
			(int)ostreamdesc.mBytesPerFrame);
	fprintf(stderr, "%5d mChannelsPerFrame\n",
			(int)ostreamdesc.mChannelsPerFrame);

	/* Check we have a Linear PCM device */
	if (ostreamdesc.mFormatID != kAudioFormatLinearPCM) {
		fprintf(stderr, "Error, format of output device is not linear PCM\n");
		return -1;
	}
	/*  get the buffersize that the default device uses for IO */
	sz = sizeof (UInt32) ;
	st = AudioDeviceGetProperty(odevice, 0, false,
			kAudioDevicePropertyBufferSize,
			&sz, &buffer_size);
	if (st) {
		printf ("AudioDeviceGetProperty (kAudioDevicePropertyBufferSize) failed.\n"); 
		return -1;
	} ;
	fprintf(stderr, "%lu buf size\n", buffer_size);

	/*  set  number of channels */
	ostreamdesc.mChannelsPerFrame = NCHANNELS;
	st = AudioDeviceSetProperty(odevice, NULL, 0, false,
			kAudioDevicePropertyStreamFormat,
			sizeof(ostreamdesc), &ostreamdesc);
	if (st) {
		printf ("Failed setting number of channels\n");
		return -1;
	} ;

	return 0;
}

typedef struct {
	int remaining;
} user_data;

static OSStatus callback(AudioDeviceID device, 
		const AudioTimeStamp* current_time, 
		const AudioBufferList* data_in, 
		const AudioTimeStamp* time_in,
		AudioBufferList* data_out, 
		const AudioTimeStamp* time_out, 
		void* client_data)
{
	int sz, i, nsamples;
	float *data;
	printf("remaining: %d\n", ((user_data*)client_data)->remaining);

	sz = (data_out->mBuffers)[0].mDataByteSize ;
	nsamples = sz / sizeof (float) ;
	data = (float*)((data_out->mBuffers)[0].mData);

	fprintf(stderr, "%ld samples\n", nsamples);
	if (NCHANNELS > 1) {
		for(i = nsamples - 1; i >= 0; --i) {
			data[i] = 2 * random() / ((float)RAND_MAX) - 1;
		}
	} else {
		fprintf(stderr, "mono not supported yet\n");
	}
	((user_data*)client_data)->remaining -= 1;
	return noErr;
}

int main()
{
	AudioDeviceID odevice;
	AudioStreamBasicDescription  ostreamdesc;
	UInt32 sz, buffer_size;
	OSStatus st;
	user_data d;

#if 0
	enumerate_devices();
	prop();
#endif

	/* Get default output device */
	sz = sizeof(AudioDeviceID);
	st = AudioHardwareGetProperty(kAudioHardwarePropertyDefaultOutputDevice,
			&sz, &odevice);

	if (odevice == kAudioDeviceUnknown) {
        fprintf(stderr, "odevice is kAudioDeviceUnknown\n");
		return -1;
	}

	/* Get stream properties of output device */
	sz = sizeof(ostreamdesc);
	st = AudioDeviceGetProperty(odevice, 0, false,
			kAudioDevicePropertyStreamFormat, &sz,
			&ostreamdesc);
	if (st) {
		fprintf(stderr, "error while getting stream format\n");
		return -1;
	}
	if (ostreamdesc.mFormatID != kAudioFormatLinearPCM) {
		fprintf(stderr, "Not linear pcm\n");
		return -1;
	}
	printf("channels: %lu, samplerate %f\n", ostreamdesc.mChannelsPerFrame,
			ostreamdesc.mSampleRate);
	ostreamdesc.mChannelsPerFrame = NCHANNELS;
	ostreamdesc.mSampleRate = SAMPLERATE;
	printf("channels: %lu, samplerate %f\n", ostreamdesc.mChannelsPerFrame,
			ostreamdesc.mSampleRate);

	st = AudioDeviceSetProperty(odevice, NULL, 0, false,
			kAudioDevicePropertyStreamFormat, sizeof
			(AudioStreamBasicDescription),
			&ostreamdesc);
	if (st != noErr) {
		fprintf(stderr, "Error setting stream props\n");
		return -1;
	}

	/* get the buffersize that the default device uses for IO */
	sz = sizeof (UInt32);
	st = AudioDeviceGetProperty(odevice, 0, false,
			kAudioDevicePropertyBufferSize, &sz, &buffer_size);
	if (st) {
		fprintf(stderr, "Error getting buffer size of default output\n");
		return -1;
	}
	fprintf(stderr, "Buffer size is %d bytes\n", buffer_size);

	st = AudioDeviceAddIOProc(odevice, callback, &d);
	if (st) {
		fprintf(stderr, "Error setting callback\n");
		return -1;
	}

	st = AudioDeviceStart(odevice, callback);
	if	(st != noErr) {
		fprintf(stderr, "Error starting device \n");
		return -1;
	}

	d.remaining = 100;
	while (d.remaining > 0) {
		usleep (10 * 1000);
	}

	return 0;
}
