#include <stdio.h>
#include <stdint.h>

#include <alsa/asoundlib.h>

int play(snd_pcm_t *pcm)
{
        int16_t buff[1024 * 16];
        int i, j;
        snd_pcm_uframes_t frames;

        for (i = 0; i < 4; ++i) {
            for (j = 0; j < 1024 * 16; ++j) {
                buff[j] = random() & 0xff;
            }
            frames = snd_pcm_writei(pcm, buff, 1024 * 16); 
            fprintf(stderr, "%lu\n", frames);
        }

        return 0;
}

int set(snd_pcm_t *pcm, snd_pcm_format_t format, snd_pcm_access_t access, 
        unsigned int channels, unsigned int samplerate)
{
        int st;

        st = snd_pcm_set_params(pcm, format, access, channels, samplerate,
                                1, 1000000);      
        if (st < 0) {
                printf("Output failed: %s\n", snd_strerror(st));
                return st;
        }

        return 0;
}

int main()
{
        snd_pcm_t *pcm;
        snd_pcm_hw_params_t *hw;

        int st;
        unsigned int rrate = 48000;
        unsigned int nc = 1;
        snd_output_t *output;

        int i, j;
        snd_pcm_sframes_t frames;

        st = snd_pcm_open(&pcm, "default", SND_PCM_STREAM_PLAYBACK, 0);
        if (st) {
                fprintf(stderr, "Error opening pcm\n");
                return -1;
        }

        st = snd_output_stdio_attach(&output, stdout, 0);
        if (st < 0) {
                printf("Output failed: %s\n", snd_strerror(st));
                return -1;
        }

        set(pcm, SND_PCM_FORMAT_S16, SND_PCM_ACCESS_RW_INTERLEAVED, 1, 44100);

        play(pcm);
        snd_pcm_drain(pcm);

        set(pcm, SND_PCM_FORMAT_S16, SND_PCM_ACCESS_RW_INTERLEAVED, 1, 8000);

        play(pcm);

        //snd_pcm_dump(pcm, output);

        snd_output_close(output);
        snd_pcm_close(pcm);

        snd_config_update_free_global();

        return 0;
}
