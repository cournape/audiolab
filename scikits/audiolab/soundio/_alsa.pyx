cdef extern from "alsa/asoundlib.h":
        ctypedef enum snd_pcm_stream_t:
               SND_PCM_STREAM_PLAYBACK
               SND_PCM_STREAM_CAPTURE
        ctypedef enum snd_pcm_access_t :
                SND_PCM_ACCESS_MMAP_INTERLEAVED
                SND_PCM_ACCESS_MMAP_NONINTERLEAVED
                SND_PCM_ACCESS_MMAP_COMPLEX
                SND_PCM_ACCESS_RW_INTERLEAVED
                SND_PCM_ACCESS_RW_NONINTERLEAVED
        ctypedef enum snd_pcm_format_t :
                SND_PCM_FORMAT_UNKNOWN
                SND_PCM_FORMAT_S8
                SND_PCM_FORMAT_U8
                SND_PCM_FORMAT_S16_LE
                SND_PCM_FORMAT_S16_BE
                SND_PCM_FORMAT_U16_LE
                SND_PCM_FORMAT_U16_BE
                SND_PCM_FORMAT_S24_LE
                SND_PCM_FORMAT_S24_BE
                SND_PCM_FORMAT_U24_LE
                SND_PCM_FORMAT_U24_BE
                SND_PCM_FORMAT_S32_LE
                SND_PCM_FORMAT_S32_BE
                SND_PCM_FORMAT_U32_LE
                SND_PCM_FORMAT_U32_BE
                SND_PCM_FORMAT_FLOAT_LE
                SND_PCM_FORMAT_FLOAT_BE
                SND_PCM_FORMAT_FLOAT64_LE
                SND_PCM_FORMAT_FLOAT64_BE
                SND_PCM_FORMAT_IEC958_SUBFRAME_LE
                SND_PCM_FORMAT_IEC958_SUBFRAME_BE
                SND_PCM_FORMAT_MU_LAW
                SND_PCM_FORMAT_A_LAW
                SND_PCM_FORMAT_IMA_ADPCM
                SND_PCM_FORMAT_MPEG
                SND_PCM_FORMAT_GSM
                SND_PCM_FORMAT_SPECIAL
                SND_PCM_FORMAT_S24_3LE
                SND_PCM_FORMAT_S24_3BE
                SND_PCM_FORMAT_U24_3LE
                SND_PCM_FORMAT_U24_3BE
                SND_PCM_FORMAT_S20_3LE
                SND_PCM_FORMAT_S20_3BE
                SND_PCM_FORMAT_U20_3LE
                SND_PCM_FORMAT_U20_3BE
                SND_PCM_FORMAT_S18_3LE
                SND_PCM_FORMAT_S18_3BE
                SND_PCM_FORMAT_U18_3LE
                SND_PCM_FORMAT_U18_3BE
                SND_PCM_FORMAT_S16
                SND_PCM_FORMAT_U16
                SND_PCM_FORMAT_S24
                SND_PCM_FORMAT_U24
                SND_PCM_FORMAT_S32
                SND_PCM_FORMAT_U32
                SND_PCM_FORMAT_FLOAT
                SND_PCM_FORMAT_FLOAT64
                SND_PCM_FORMAT_IEC958_SUBFRAME
        char* snd_strerror(int error)
        int snd_card_next(int *icard)
        int snd_card_get_name(int icard, char** name)

cdef extern from "stdlib.h":
        ctypedef unsigned long size_t
        void free(void *ptr)
        void *malloc(size_t size)
        void *realloc(void *ptr, size_t size)
        size_t strlen(char *s)
        char *strcpy(char *dest, char *src)

cdef extern from "Python.h":
        object PyString_FromStringAndSize(char *v, int len)

class AlsaException(Exception):
        pass

def card_indexes():
        """Returns a list containing index of cards recognized by alsa."""
        cdef int icur = -1

        cards = []
        while 1:
                st = snd_card_next(&icur)
                if st < 0:
                        raise AlsaException("Could not get next card")
                if icur < 0:
                        break
                cards.append(icur)
        return tuple(cards)

def card_name(index):
        """Get the name of the card corresponding to the given index."""
        cdef char* sptr
        st = snd_card_get_name(index, &sptr)
        if st < 0:
                raise AlsaException("Error while getting card name %d: alsa error "\
                                    "was %s" % (index, snd_strerror(st)))
        else:
                cardname = PyString_FromStringAndSize(sptr, len(sptr))
                free(sptr)
        return cardname
