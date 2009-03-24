Obsolete API
============

This section documents the old, deprecated API.

        **NOTE** The old sndfile and formatinfo has been obsoleted in 0.10.
        Those classes were based on ctypes code, the new code is based on
        cython, and is more reliable, as well as more conformant to python
        conventions. In 0.10, the sndfile and formatinfo classes are thin
        wrappers around the Sndfile and Format classes, and you are advised to
        use those instead.

Overview
--------

The following code shows you how to open a file for read, reading the first
1000 frames, and closing it:

.. literalinclude:: examples/obsolete/quick1.py

Opening a file and getting its parameters
-----------------------------------------

Once imported, audiolab gives you access the sndfile class, which is the class
of audiolab use to open audio files.  You create a sndfile instance when you
want to open a file for reading or writing (the file test.flac is included in
the audiolab package, in the test_data directory):

.. literalinclude:: examples/obsolete/usage1.py

Prints you the information related to the file, like its sampling rate, the
number of frames, etc... You can of course get each parameter individually by
using the corresponding sndfile.get* accessors.

Importing audio data
--------------------

Now that we've opened a file, we would like to read its audio content, right ?
For now, you can only import the data as floating point data, float  (32 bits)
or double (64 bits). The function sndfile.read_frames read n frames, where a
frame contains a sample of each channel (one in mono, 2 in stereo, etc...):

.. literalinclude:: examples/obsolete/usage2.py

The above code import 10000 frames, and plot the first channel using matplotlib
(see below). A frame holds one sample from each channel: 1000 frames of a
stereo file is 2000 samples. Each channel is one column of the numpy array. The
read functions follow numpy conventions, that is by default, the data are read
as double, but you can give a dtype argument to the function.

The format class
----------------

When opening a file for writing, you need to give various parameters related to
the format such as the file format, the encoding.  The format class is used to
create valid formats from those parameters  By default, the format class
creates a format object with file type wav, and 16 bits pcm encoding:

.. literalinclude:: examples/obsolete/format1.py

prints back "Major Format: AIFF (Apple/SGI), Encoding Format: U-Law" and "Major
Format: SF (Berkeley/IRCAM/CARL), Encoding Format: 32 bit float".

Writing data to a file
----------------------

Opening a file for writing is a bit more complicated than reading; you need to
say which format you are requesting, the number of channels and the sampling
rate (in Hz) you are requesting; all those information are mandatory !  The
class format is used to build a format understandable by libsndfile from
'user-friendly' values. Let's see how it works.

.. literalinclude:: examples/obsolete/write1.py

