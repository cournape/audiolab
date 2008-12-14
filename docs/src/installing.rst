=========================
Download and installation
=========================

Supported platforms
===================

Audiolab has been run succesfully on the following platforms:

    - linux ubuntu (32 and 64 bits)
    - windows XP (32 bits)
    - Mac OS X (10.5)

I would be interested to hear anyone who succeesfully used it on other
platforms.

Download
========

audiolab is part of scikits: its source can be downloaded directly from the
scikits svn repository::

	svn co http://svn.scipy.org/svn/scikits/trunk/audiolab

Requirements
============

audiolab requires the following softwares:

 - a python interpreter.
 - libsndfile
 - numpy (any version >= 1.0 should work).
 - setuptools

On Ubuntu, you can install the dependencies as follow::

        sudo apt-get install python-dev python-numpy python-setuptools libsndfile-dev

Optional
========

Audiolab can optionally install audio backends. For now, only alsa is
supported, for linux audio support. You need alsa headers for this to work; on
Ubuntu, you can install them with the following command::

        sudo apt-get install libasound2-dev

Installation
============

For unix users, if libsndfile is installed in standart location (eg /usr/lib,
/usr/local/lib), the installer should be able to find them automatically, and
you only need to do a "python setup.py install". In other cases, you need to
create a file site.cfg to set the location of libsndfile and its header (there
are site.cfg examples which should give you an idea how to use them on your
platform).

License
=======

audiolab is released under the LGPL, which forces you to release back the
modifications you may make in the version of audiolab you are distributing, but
you can still use it in closed softwares, as long as you don't use a modified
version of it. The soundio module to output data onto sound devices is under
the BSD, though.

