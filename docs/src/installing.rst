=========================
Download and installation
=========================

Supported platforms
===================

Audiolab has been run succesfully on the following platforms:

    - linux ubuntu (32 and 64 bits) and RHEL 5 (32 and 64 bits)
    - windows XP (32 bits)
    - Mac OS X (10.5, intel)
    - OpenSolaris (x86)

I would be interested to hear anyone who succeesfully used it on other
platforms.

Download
========

Releases are available on Pypi:

        http://pypi.python.org/pypi/scikits.audiolab/

Audiolab is part of scikits, and its source are kept on `github
<http://github.com/cournape/audiolab>`_. Docs for the development version of
audiolab can be found on `gh-pages <http://cournape.github.com/audiolab>`_.

Install from binaries
=====================

Requirements
------------

To install the binaries, audiolab requires the following softwares:

 - a python interpreter.
 - numpy (any version >= 1.2 should work).

Binaries
--------

Binaries for Mac OS X and Windows are provided on Pypi - they are statically
linked to libsndfile (so that you don't need to install your own version of
libsndfile first). If you are not familiar with building from sources, you are
strongly advised to use those.

Installation from sources
=========================

Requirements
------------

audiolab requires the following softwares:

 - a python interpreter.
 - libsndfile
 - numpy (any version >= 1.2 should work).
 - setuptools

On Ubuntu, you can install the dependencies as follow::

        sudo apt-get install python-dev python-numpy python-setuptools libsndfile-dev

Optional
--------

Audiolab can optionally install audio backends. For now, only alsa (Linux) and
Core Audio (Mac OS X) are supported. On Linux, you need alsa headers for this
to work; on Ubuntu, you can install them with the following command::

        sudo apt-get install libasound2-dev

For Mac OS X, you need the CoreAudio framework, available on the Apple website.

Build
-----

For unix users, if libsndfile is installed in standart location (eg /usr/lib,
/usr/local/lib), the installer should be able to find them automatically, and
you only need to do a "python setup.py install". In other cases, you need to
create a file site.cfg to set the location of libsndfile and its header (there
are site.cfg examples which should give you an idea how to use them on your
platform).

License
=======

Audiolab is released under the LGPL, which forces you to release back the
modifications you may make in the version of audiolab you are distributing, but
you can still use it in closed softwares, as long as you don't use a modified
version of it. The soundio module to output data onto sound devices is under
the BSD, though (so you can use it, modify it in close source software without
publishing the sources).

Audiolab is under the LGPL because libsndfile itself, and as such, a BSD
audiolab is of little value.
