#include <stdio.h>

#include <alsa/asoundlib.h>

int main()
{
        snd_pcm_t *pcm;
        snd_pcm_hw_params_t *hw;

        int st;

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

        snd_pcm_hw_params_free(hw);
        snd_pcm_close(pcm);

        snd_config_update_free_global();

        return 0;
}
