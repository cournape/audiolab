#include <stdio.h>

#include <alsa/asoundlib.h>

int main()
{
        snd_pcm_t *pcm;
        snd_pcm_hw_params_t *hw;

        int st;
        unsigned int rrate = 44100;
        snd_output_t *output;

        st = snd_pcm_open(&pcm, "default", SND_PCM_STREAM_PLAYBACK, 0);
        if (st) {
                fprintf(stderr, "Error opening pcm\n");
                return -1;
        }

        st = snd_pcm_hw_params_malloc(&hw);
        if (st) {
                fprintf(stderr, "Error while allocating hw\n");
                return -1;
        }

        st = snd_pcm_hw_params_any(pcm, hw);
        if (st) {
                fprintf(stderr, "Error while allocating hw\n");
                return -1;
        }

        st = snd_pcm_hw_params_set_access(pcm, hw, SND_PCM_ACCESS_RW_INTERLEAVED);
        if (st) {
                fprintf(stderr, "Error while allocating hw\n");
                return -1;
        }

        st = snd_pcm_hw_params_set_rate_near(pcm, hw, &rrate, 0);
        if (st) {
                fprintf(stderr, "Error while allocating hw\n");
                return -1;
        }
        fprintf(stdout, "rate is %d\n", rrate);

        st = snd_pcm_hw_params(pcm, hw);
        if (st) {
                fprintf(stderr, "Error while allocating hw\n");
                return -1;
        }

        //st = snd_output_stdio_attach(&output, stdout, 0);
        //if (st < 0) {
        //        printf("Output failed: %s\n", snd_strerror(st));
        //        return 0;
        //}
        st = snd_output_buffer_open(&output);
        if (st < 0) {
                printf("Output buffer open failed: %s\n", snd_strerror(st));
                return 0;
        }
        char* buf;
        snd_pcm_dump(pcm, output);
        st = snd_output_buffer_string(output, &buf);
        fprintf(stdout, "%d chars\n", st);
        fprintf(stdout, "%s", buf);

        //snd_output_close(output);
        //snd_pcm_hw_params_free(hw);
        snd_pcm_close(pcm);

        snd_config_update_free_global();

        return 0;
}
