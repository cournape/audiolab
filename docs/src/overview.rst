========
Overview
========

For simple usage, the matlab-like API is the simplest to use. For example, if
you want to read a wav file, you can do it in one function call

.. literalinclude:: examples/over_matlab.py

This read the file test.wav, and returns the data, sampling rate as well as the
encoding as a string. Similar function exists for writing, and for other
formats: wav, aiff, au, ircam, ogg and flac formats are supported through this
simple API.

Sndfile class
=============

For more control (for example writing with a non default encoding, controlling
output array dtype), the Sndfile class should be used. Internally, the simple
functions are just wrappers around this class. Let's see a simple example on
how to use the Sndfile class for reading:

.. literalinclude:: examples/over1.py

As you can see the usage for reading is straightforward. A Sndfile instance
first created, and the instance is used for reading, as well as for querying
meta-data about the file, like the sampling rate or the number of channels.

The read_frames method can optionally take a dtype argument like many numpy
functions, to select the dtype of the output array. The exact semantics are
more complicated than with numpy though, because of audio encoding
specifies (see encoding section).

Writing audio file from data in numpy arrays is a bit more complicated, because
you need to tell the Sndfile class about the file type, encoding and
endianness, as well as the sampling rate and number of channels. For
simplicity, the file format, encoding and endianness is controlled from an
helper class, Format:

.. literalinclude:: examples/over2.py

The Format class can be used to control more precisely the encoding or the
endianness of the written file:

.. literalinclude:: examples/over3.py

Not all file formats and encodings combinations are possible. Also, the exact
number of file formats and encodings available depend on your version of
libsndfile. Both can be queried at runtime with the functions
available_file_formats and available_encodings. The following example print all
available file formats and encodings (the output depends on your installed
libsndfile):

.. literalinclude:: examples/over_available.py

Sound output
============

audiolab now has some facilities to output sound from numpy arrays:

.. literalinclude:: examples/over_play.py

