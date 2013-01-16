#include <alsa/asoundlib.h>

int main()
{
        int st;
        int card = -1;
        const char iface[] = "pcm";
        char** hints;

        fprintf(stderr, "Alsa API version is %s\n", snd_asoundlib_version());

        st = snd_device_name_hint(card, iface, &hints);
        card = 0;
        while(hints[card] != NULL) {
                fprintf(stderr, "hints: %s\n", hints[card]);
                ++card;
        }

        return 0;
}
