============
Introduction
============

.. _scipy: http://www.scipy.org
.. _libsndfile: http://www.mega-nerd.com/libsndfile/

For people doing audio processing, it is useful to be able to import data from
audio files, and export them back, as well as listening to the results of some
processing; matlab have functions such as wavread, wavwrite, soundsc, etc...
for that purposes.  The goal of audiolab is to give those capabilities to the
`scipy`_ environment by wrapping the excellent library `libsndfile`_ from Erik
Castro de Lopo. Audiolab supports all format supported by libsndfile, including
wav, aiff, ircam files, flac (an open source lossless compressed format) and
ogg vorbist (an open source compressed format - simlar to MP3 without the
license issues); see `here <http://www.mega-nerd.com/libsndfile/#Features">`_
for a complete list.

The main features of audiolab are:
        - reading all formats supported by sndfile directly into numpy arrays.
        - writing all formats supported by sndfile directly from numpy arrays.
        - A matlab-like API (ala wavread) for some file formats. Wav, aiff,
          flac, au, and ogg formats are supported.
        - A play function to output data from numpy array into the sound device
          of your computer (Only ALSA for linux and CoreAudio for Mac OS X is
          implemented ATM).

    **Note**: The library is still in flux: the API can still change before the
    1.0 version. That baing said, the version 0.10 was a major change, and I
    don't expect any more major changes.

    **Note**: The online version of this document is not always up to date. The
    pdf included in the package is the reference, and always in sync with the
    package. If something does not work, please refer first to the pdf included in
    the package.

