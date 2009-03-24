========
Full API
========

Audio file IO
=============

.. currentmodule:: scikits.audiolab

The :class:`~Format` class
--------------------------

The Format class is used to control meta-data specific to one type of audio
file (file format, encoding and endianness). It is mainly useful when writing
files or reading raw (header-less) audio files. A Format instance can be
queried for its related meta-data:

        >>> from scikits.audiolab import Format
        >>> a = Format() # By default, 16 bits PCM wav file
        >>> print a # Will print a detail description of the format

.. autoclass:: Format

.. attribute:: Format.file_format

        Returns the file format.

.. attribute:: Sndfile.file_format_description

        Returns the full description of the file format.

.. attribute:: Sndfile.encoding

        Returns the encoding.

.. attribute:: Sndfile.encoding_description

        Returns the full description of the encoding.

.. attribute:: Sndfile.endianness

        Returns the endianness.

The following two functions can be used to query the available formats and
encodings. The exact list of formats depend on the libsndfile audiolab was
built against.

        >>> from scikits.audiolab import available_encodings
        >>> # List encodings supported for the wav format
        >>> print available_encodings('wav')

.. autofunction:: available_file_formats
.. autofunction:: available_encodings

The :class:`~Sndfile` class
---------------------------

Sndfile is the main class for audio file IO.

.. autoclass:: Sndfile

Read methods
~~~~~~~~~~~~

.. automethod:: Sndfile.read_frames

Write methods
~~~~~~~~~~~~~

.. automethod:: Sndfile.write_frames
.. automethod:: Sndfile.sync

Meta-data
~~~~~~~~~

.. attribute:: Sndfile.samplerate

        Returns the sampling rate of the file

.. attribute:: Sndfile.channels

        Returns the number of channels

.. attribute:: Sndfile.frames

        Returns the number of frames in the file

.. attribute:: Sndfile.format

        Returns the Format instance attached to the file.

Encoding and array dtype
~~~~~~~~~~~~~~~~~~~~~~~~

The most common encoding for common audio files like wav of aiff is signed 16
bits integers. Sndfile and hence audiolab enables many more encodings like
unsigned 8 bits, floating point. Generally, when using the data for processing,
the encoding of choice is floating point; the exact type is controlled through
the array dtype. When the array dtype and the file encoding don't match, there
has to be some conversion.

When converting between integer PCM formats of differing size (i.e. both file
encoding and input/output array dtype is an integer type), the Sndfile class
obeys one simple rule:

        * Whenever integer data is moved from one sized container to another
          sized container, the most significant bit in the source container
          will become the most significant bit in the destination container.

When either the encoding is an integer but the numpy array dtype is a float
type, different rules apply. The default behavior when reading floating point
data (array dtype is float) from a file with integer data is normalization.
Regardless of whether data in the file is 8, 16, 24 or 32 bit wide, the data
will be read as floating point data in the range [-1.0, 1.0].  Similarly, data
in the range [-1.0, 1.0] will be written to an integer PCM file so that a data
value of 1.0 will be the largest allowable integer for the given bit width.

Sound output
============

audiolab now has some facilities to output sound from numpy arrays: the
function play is a wrapper around a platform-specific audio backend. For now,
only ALSA backend (Linux) and Core Audio backend (Mac OS X) are implemented.
Other backends (for windows, OSS for Solaris/BSD) may be added later, although
it is not a priority for me. Patches are welcomed, particularly for windows.

.. autofunction:: play

