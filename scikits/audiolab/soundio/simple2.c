#include <stdio.h>
#include <stdint.h>

#include <alsa/asoundlib.h>

int main()
{
        snd_pcm_t *pcm;
        snd_pcm_hw_params_t *hw;

        int st;
        unsigned int rrate = 48000;
        unsigned int nc = 1;
        snd_output_t *output;

        uint8_t buff[1024 * 16];
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

        st = snd_pcm_set_params(pcm, 
                                SND_PCM_FORMAT_S16, 
                                SND_PCM_ACCESS_RW_INTERLEAVED, 
                                nc, 
                                rrate,
                                1,
                                1000000);      
        if (st < 0) {
                printf("Output failed: %s\n", snd_strerror(st));
                return -1;
        }
        snd_pcm_dump(pcm, output);

        fprintf(stderr, "SND_PCM_FORMAT_U8 : %d\n", SND_PCM_FORMAT_U8);
        fprintf(stderr, "SND_PCM_FORMAT_S16 : %d\n", SND_PCM_FORMAT_S16);
        fprintf(stderr, "SND_PCM_FORMAT_FLOAT : %d\n", SND_PCM_FORMAT_FLOAT);
        fprintf(stderr, "SND_PCM_ACCESS_RW_INTERLEAVED : %d\n", SND_PCM_ACCESS_RW_INTERLEAVED);
        for (i = 0; i < 16; ++i) {
            for (j = 0; j < 1024 * 16; ++j) {
                buff[j] = random() & 0xff;
            }
            frames = snd_pcm_writei(pcm, buff, 1024 * 16); 
            fprintf(stderr, "%u\n", frames);
        }
        snd_output_close(output);
        snd_pcm_close(pcm);

        snd_config_update_free_global();

        return 0;
}
