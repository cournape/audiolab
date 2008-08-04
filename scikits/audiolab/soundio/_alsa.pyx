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

        ctypedef struct snd_pcm_t
        # XXX: how to make sure the typedef is OK ?
        ctypedef unsigned long snd_pcm_uframes_t

        int snd_pcm_open(snd_pcm_t **, char*, int, int)
        int snd_pcm_close(snd_pcm_t *)
        int snd_pcm_drain(snd_pcm_t *)

        int snd_pcm_set_params(snd_pcm_t *, snd_pcm_format_t,
                        snd_pcm_access_t, unsigned int,
                        unsigned int, int, unsigned int)

        int snd_pcm_writei(snd_pcm_t *, void*, snd_pcm_uframes_t)

        char* snd_strerror(int error)

        int snd_card_next(int *icard)
        int snd_card_get_name(int icard, char** name)
        char* snd_asoundlib_version()

cdef extern from "numpy/arrayobject.h":
        ctypedef int intp
        ctypedef extern class numpy.ndarray [object PyArrayObject]:
                cdef char *data
                cdef int nd
                cdef intp *dimensions
                cdef intp *strides
                cdef int flags

cdef extern from "stdlib.h":
        ctypedef unsigned long size_t
        void free(void *ptr)
        void *malloc(size_t size)
        void *realloc(void *ptr, size_t size)
        size_t strlen(char *s)
        char *strcpy(char *dest, char *src)

cdef extern from "stdint.h":
        ctypedef unsigned short int16_t

cdef extern from "Python.h":
        object PyString_FromStringAndSize(char *v, int len)

class AlsaException(Exception):
        pass

def asoundlib_version():
        return snd_asoundlib_version()

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

cdef class _PCM:
        cdef snd_pcm_t* pcmhdl
        cdef public char* name

        def __new__(self, device = "default", stream = SND_PCM_STREAM_PLAYBACK):
                self.pcmhdl = NULL

                st = snd_pcm_open(&self.pcmhdl, device, stream, 0)
                if st < 0:
                        raise AlsaException("Cannot open device %s: %s" % (device, snd_strerror(st)))

        def __init__(self, device = "default", stream = SND_PCM_STREAM_PLAYBACK):
                self.name = device

        def __dealloc__(self):
                if self.pcmhdl:
                        snd_pcm_close(self.pcmhdl)

cdef class Device:
        cdef _PCM pcm
        cdef unsigned int samplerate
        # XXX: set property instead
        cdef public unsigned int channels
        cdef snd_pcm_format_t format
        cdef snd_pcm_access_t access
        def __init__(self, samplerate = 48000, channels = 1,
                     format = SND_PCM_FORMAT_S16,
                     access = SND_PCM_ACCESS_RW_INTERLEAVED):
                self.pcm = _PCM()

                self.samplerate = samplerate
                self.channels = channels

                self.access = access
                self.format = format

                st = snd_pcm_set_params(self.pcm.pcmhdl, format, access, channels,
                                        samplerate, 1, 1000000)
                if st < 0:
                        raise AlsaException()

        def play_short(self, ndarray input):
                cdef int16_t* p = <int16_t*>input.data
                cdef int16_t* buff = NULL
                #cdef int n = input.dimensions[0]
                cdef int n = input.dimensions[0]
                cdef int nb = n / 1024 / 16
                cdef snd_pcm_uframes_t bufsz = 1024 * 16

                assert self.format == SND_PCM_FORMAT_S16
                assert self.access == SND_PCM_ACCESS_RW_INTERLEAVED

                for i from 0 <= i  < nb:
                        st =  snd_pcm_writei(self.pcm.pcmhdl, &p[i * bufsz], bufsz)
                        if not st == bufsz:
                                print "Error while writing to device", st
                                print snd_strerror(st)

                snd_pcm_drain(self.pcm.pcmhdl)

        def _get_name(self):
                return self.pcm.name
        name = property(_get_name)
