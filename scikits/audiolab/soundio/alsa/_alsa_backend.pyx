import numpy as np
cimport numpy as cnp
cimport stdlib
cimport python_exc
from alsa cimport *

cdef int BUFFER_TIME  = 500000
cdef int PERIOD_TIME  = 0

cdef extern from "alsa/asoundlib.h":
        # This is needed here because it is a macro and is not recognized by
        # gccxml it seems
        int snd_pcm_hw_params_alloca(snd_pcm_hw_params_t **)
        int snd_pcm_sw_params_alloca(snd_pcm_sw_params_t **)

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
                stdlib.free(sptr)
        return cardname

cdef struct format_info:
        # number of channels
        int nchannel
        # Rate (samples/s -> Hz)
        int rate
        # Bits per sample
        int nbits
        # Byte format
        int byte_fmt

cdef class AlsaDevice:
        cdef snd_pcm_t *handle
        def __init__(AlsaDevice self, unsigned rate=48000, int nchannels=1):
                cdef int st
                cdef unsigned int psize, bsize
                cdef format_info info

                info.rate = rate
                info.nchannel = nchannels

                self.handle = <snd_pcm_t*>0
                st = snd_pcm_open(&self.handle, "default", SND_PCM_STREAM_PLAYBACK, 0)
                if st < 0:
                        raise AlsaException("Fail opening 'default'")

                set_hw_params(self.handle, info, &psize, &bsize)
                print "Period size is", psize, ", Buffer size is", bsize

                set_sw_params(self.handle, psize, bsize)

        def play(AlsaDevice self, cnp.ndarray input):
                self._play(input)

        cdef int _play(AlsaDevice self, cnp.ndarray input) except -1:
                cdef cnp.ndarray[cnp.int16_t, ndim=2] tx
                cdef int nr, i, nc
                cdef int bufsize = 1024
                cdef int err = 0

                if not input.ndim == 2:
                        raise ValueError("Only rank 2 for now")
                else:
                        nc = input.shape[1]
                        if not nc == 2:
                                raise ValueError("Only stereo for now")

                tx = np.empty((bufsize, nc), dtype=np.int16)
                nr = input.size / nc / bufsize

                st = snd_pcm_prepare(self.handle)
                if st:
                        raise AlsaException("Error while preparing the pcm device")

                for i in range(nr):
                        err = python_exc.PyErr_CheckSignals()
                        if err != 0:
                                break
                        tx = (32568 * input[i * bufsize:i * bufsize + bufsize, :]).astype(np.int16)
                        st = snd_pcm_writei(self.handle, <void*>tx.data, bufsize)
                        if st < 0:
                                raise AlsaException("Error in writei")

                if err:
                        print "Got SIGINT: draining the pcm device... "
                        snd_pcm_drain(self.handle)
                        return -1
                snd_pcm_drain(self.handle)
                return 0

        def __dealloc__(AlsaDevice self):
                if self.handle:
                        snd_pcm_close(self.handle)

cdef set_hw_params(snd_pcm_t *hdl, format_info info, unsigned int* period_size, unsigned int *buffer_size):
        cdef unsigned int nchannels, buftime, pertime, samplerate
        cdef snd_pcm_hw_params_t *params
        cdef int st
        cdef snd_pcm_access_t access
        cdef snd_pcm_format_t format

        access = SND_PCM_ACCESS_RW_INTERLEAVED
        buftime = BUFFER_TIME
        pertime = PERIOD_TIME

        nchannels = info.nchannel
        samplerate = info.rate
        format = SND_PCM_FORMAT_S16_LE

        snd_pcm_hw_params_alloca(&params)
        st = snd_pcm_hw_params_any(hdl, params)
        if st < 0:
                raise AlsaException("Error in _any")

        st = snd_pcm_hw_params_set_access(hdl, params, access)
        if st < 0:
                raise AlsaException("Error in _set_access")

        st = snd_pcm_hw_params_set_format(hdl, params, format)
        if st < 0:
                raise AlsaException("Error in _set_format")

        st = snd_pcm_hw_params_set_channels(hdl, params, nchannels)
        if st < 0:
                raise AlsaException("Error in _set_channels")

        st = snd_pcm_hw_params_set_rate_near(hdl, params, &samplerate, 0)
        if st < 0:
                raise AlsaException("Error in _set_rate_near")

        st = snd_pcm_hw_params_set_buffer_time_near(hdl, params, &buftime, 0)
        if st < 0:
                raise AlsaException("Error in _set_buffer_near")

        st = snd_pcm_hw_params_set_period_time_near(hdl, params, &pertime, 0)
        if st < 0:
                raise AlsaException("Error in _set_period_time_near")

        st = snd_pcm_hw_params(hdl, params)
        if st < 0:
                raise AlsaException("Error in applying hw params")

        st = snd_pcm_hw_params_get_period_size(params, period_size, 0)
        if st < 0:
                raise AlsaException("Error in get_period_sizse")

        st = snd_pcm_hw_params_get_buffer_size(params, buffer_size)
        if st < 0:
                raise AlsaException("Error in get_buffer_sizse")

cdef set_sw_params(snd_pcm_t *hdl, unsigned int period_size, unsigned int buffer_size):
        cdef snd_pcm_sw_params_t *params

        snd_pcm_sw_params_alloca(&params)

        st = snd_pcm_sw_params_current(hdl, params)
        if st < 0:
                raise AlsaException("Error in _current")

        st = snd_pcm_sw_params_set_start_threshold(hdl, params, period_size)
        if st < 0:
                raise AlsaException("Error in _set_start_threshold")

        st = snd_pcm_sw_params_set_avail_min(hdl, params, period_size)
        if st < 0:
                raise AlsaException("Error in _set_avail_min")

        st = snd_pcm_sw_params(hdl, params)
        if st < 0:
                raise AlsaException("Error in applying sw params")
