#
# Copyright (C) 2008 Cournapeau David <cournape@gmail.com>
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#      * Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#      * Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in
#        the documentation and/or other materials provided with the
#        distribution.
#      * Neither the author nor the names of any contributors may be used
#        to endorse or promote products derived from this software without
#        specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
#  TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import warnings

import numpy as np

if sys.platform[:5] == 'linux':
    BACKEND = 'ALSA'
elif sys.platform[:6] == 'darwin':
    BACKEND = 'CoreAudio'
else:
    BACKEND = None

if BACKEND == 'ALSA':
    try:
        from scikits.audiolab.soundio._alsa_backend import AlsaDevice
    except ImportError, e:
        warnings.warn("Could not import alsa backend; most probably, "
                      "you did not have alsa headers when building audiolab")

    def _play(input, fs):
        if input.ndim == 1:
            input = input[np.newaxis, :]
            nc = 1
        elif input.ndim == 2:
            nc = input.shape[0]
        else:
            raise ValueError, \
                  "Only input of rank 1 and 2 supported for now."

        dev = AlsaDevice(fs=fs, nchannels=nc)
        dev.play(input)
elif BACKEND == 'CoreAudio':
    try:
        from scikits.audiolab.soundio.macosx_backend import CoreAudioDevice
    except ImportError, e:
        print e
        warnings.warn("Could not import CoreAudio backend; most probably, "
                      "you did not have CoreAudio headers when building audiolab")

    def _play(input, fs):
        if input.ndim == 1:
            input = input[np.newaxis, :]
            nc = 1
        elif input.ndim == 2:
            nc = input.shape[0]
        else:
            raise ValueError, \
                  "Only input of rank 1 and 2 supported for now."

        dev = CoreAudioDevice(fs=fs, nchannels=nc)
        dev.play(input)
else:
    def _play(input, fs):
        raise NotImplementedError, \
              "No Backend implemented for you platform " \
              "(detected platform is: %s)" % sys.platform

def play(input, fs=44100):
    """Play the signal in vector input to the default output device.

    Only floating point input are supported: input is assumed to be in the
    -1..1 range. Any values outside this range will be clipped by the device.

    Parameters
    ----------
    input: array
        input signal of rank 2. Each row is assumed to be one channel.
    fs: int
        sampling rate (in Hz)

    Notes
    -----
    It will fail if the sampling rate is not supported by your device. In
    particular, no automatic resampling is done. Mono signals are doubled for
    fake stereo for the CoreAudio framework, as it seemse CoreAudio does not
    handle mono on its own.
    """
    return _play(input, fs)
