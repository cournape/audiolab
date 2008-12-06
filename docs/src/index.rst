..
    restindex
        page-title: audiolab
        crumb: audiolab
        link-title: audiolab
        encoding: utf-8
        output-encoding: None
        file: audiolab1.png
        file: quick1.py
        file: usage1.py
        file: usage2.py
        file: format1.py
        file: format2.py
        file: write1.py
        file: matlab1.py
        file: audiolab.pdf
    /restindex

.. vim:syntax=rest
.. Last Change: Sun Dec 07 01:00 AM 2008 J

==========================================================
Audiolab, a python package to make noise with numpy arrays
==========================================================

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
        - reading all formats supported by sndfile, and put the data into numpy
          arrays. The array dtype can be selected
        - writing all formats supported by sndfile from data in numpy arrays.
          The array dtype can be selected
        - A matlab-like API for some file formats, like wavread. Wav, aiff,
          flac, au, and ogg formats are supported.
        - A play function to output data from numpy array into the sound device
          of your computer (Only ALSA for linux is implemented ATM).

    **Note**: The library is still in flux: the API can still change before the
    1.0 version.

    **Note**: The online version of this document is not always up to date. The
    pdf included in the package is the reference, and always in sync with the
    package. If something does not work, please refer first to the pdf included in
    the package.

.. contents:: Tables of contents

Download and installation
=========================

Supported platforms
-------------------

Audiolab has been run succesfully on the following platforms:

    - linux ubuntu (32 and 64 bits)
    - windows XP (32 bits)
    - Mac OS X (10.5)

I would be interested to hear anyone who succeesfully used it on other
platforms.

Download
--------

audiolab is part of scikits: its source can be downloaded directly from the
scikits svn repository::

	svn co http://svn.scipy.org/svn/scikits/trunk/audiolab

Requirements
------------

audiolab requires the following softwares:

 - a python interpreter.
 - libsndfile
 - numpy (any version >= 1.0 should work).
 - setuptools

On Ubuntu, you can install the dependencies as follow::

        sudo apt-get install python-dev python-numpy python-setuptools libsndfile-dev

Optional
--------

Audiolab can optionally install audio backends. For now, only alsa is
supported, for linux audio support. You need alsa headers for this to work; on
Ubuntu, you can install them with the following command::

        sudo apt-get install libasound2-dev

Installation
------------

For unix users, if libsndfile is installed in standart location (eg /usr/lib,
/usr/local/lib), the installer should be able to find them automatically, and
you only need to do a "python setup.py install". In other cases, you need to
create a file site.cfg to set the location of libsndfile and its header (there
are site.cfg examples which should give you an idea how to use them on your
platform).

License
-------

audiolab is released under the LGPL, which forces you to release back the
modifications you may make in the version of audiolab you are distributing, but
you can still use it in closed softwares, as long as you don't use a modified
version of it. The soundio module to output data onto sound devices is under
the BSD, though.

Usage
=====

Overview
--------

For simple usage, the matlab-like API is the simplest to use. For example, if
you want to read a wav file, you can do it in one function call

.. literalinclude:: examples/over_matlab.py

This read the file test.wav, and returns the data, sampling rate as well as the
encoding as a string. Similar function exists for writing, and for other
formats: wav, aiff, au, ircam, ogg and flac formats are supported through this
simple API.

Sndfile class
~~~~~~~~~~~~~

For more control (for example writing with a non default encoding, controling
output array dtype), the Sndfile class should be used. Internally, the simple
functions are just wrappers around this class. Let's see a simple example on
how to use the Sndfile class for reading:

.. literalinclude:: examples/over1.py

As you can see the usage for reading is straightfoward. A Sndfile instance
first created, and the instance is used for reading, as well as for quering
meta-data about the file, like the sampling rate or the number of channels.

The read_frames method can optionally take a dtype argument like many numpy
functions, to select the dtype of the output array. The exact semantics are
more complicated than with numpy though, because of audio encoding
specificities (see encoding section). 

Writing audio file from data in numpy arrays is a bit more complicated, because
you need to tell the Sndfile class about the file type, encoding and
endianness, as well as the sampling rate and number of channels. For
simplicity, the file format, encoding and endianness is controled from an
helper class, Format:

.. literalinclude:: examples/over2.py

The Format class can be used to control more precisely the encoding or the
endianness of the written file:

.. literalinclude:: examples/over3.py

Sound output
~~~~~~~~~~~~

audiolab also have some facilities to output sound from numpy arrays:

.. literalinclude:: examples/over_play.py

The function play is a wrapper around a platform-specific audio backend. For
now, only ALSA backend (Linux) is implemented. Core Audio backend for support
on Mac OS X will be soon available. Other backends (for windows, OSS for
Solaris/BSD) may be added later.

.. Encoding and array dtype
.. ------------------------
.. 
.. Common audio files are encoded in fixed point (integers): for example, the
.. usual wav files are encoded in 16 bits, and a sample can take any value in the
.. [-32768, 32768] range. Some audio files also support floating point encoding,
.. in which case the data are conventionally normalized in the [-1..1] range. 
..        
.. There is a difference though: depending on the dtype, the values in the array
.. can be vastly different: if the dtype is a floating point type, all values are
.. between -1 and 1, if the dtype It is becuase audiolab follows the same
.. convention as libsndfile - which is the most used convention for pcm audio data
.. representation
.. 
.. Matlab-like API
.. ---------------
.. 
.. audiolab also have a matlab-like API for audio IO. Its usage is as similar as it
.. can get using python:
.. 
.. .. literalinclude:: examples/matlab1.py
.. 
.. Sound output
.. ------------
.. 
.. New feature in 0.9: only ALSA (Linux sound API) has been implemented so far.
.. 
.. .. literalinclude:: examples/play.py

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

Prints you the informations related to the file, like its sampling rate, the
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
rate (in Hz) you are requesting; all thoses information are mandatory !  The
class format is used to build a format understable by libsndfile from
'user-friendly' values. Let's see how it works.

.. literalinclude:: examples/obsolete/write1.py

Known bugs:
===========

 - the function supported_* are broken (they never worked correctly). This will
   be fixed for audiolab 0.10
 - there seems to be a problem when using libsndfile fseek facilities with flac
   files (which are necessary for the functions flacread/flacwrite). The
   problem seems to be with libFLAC; for this reason, seek in flac files is not
   enabled by default for now. See FLAC_SUPPORT.txt for more informations.

TODO
====

audiolab is still in early stages. Before a release, I would like to implement the
follwings:

 - support (at least some) meta-data embedded in some audio files format.
 - support the libsndfile's error system
 - player on all major plateforms (at least linux/windows/max OS X)
