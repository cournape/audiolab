cdef extern from "alsa/asoundlib.h":
        ctypedef enum SND_PCM_STREAM :
               SND_PCM_STREAM_PLAYBACK
               SND_PCM_STREAM_CAPTURE
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

if __name__ == '__main__':
        cards = [card_name(i) for i in card_indexes()]
        print cards
