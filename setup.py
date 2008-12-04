#! /usr/bin/env python
# Last Change: Thu Dec 04 07:00 PM 2008 J

# Copyright (C) 2006-2007 Cournapeau David <cournape@gmail.com>
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option) any
# later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this library; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

# TODO:
#   - check how to handle cmd line build options with distutils and use
#   it in the building process

descr   = """ audiolab is a small python package to import data from audio
files to numpy arrays and export data from numpy arrays to audio files. It uses
libsndfile from Erik Castro de Lopo for the underlying IO, which supports many
different audio formats: http://www.mega-nerd.com/libsndfile/

For now, the python api for audio IO should be stable; a matlab-like API is
also available for quick read/write (ala wavread, wavwrite, etc...). For 1.0
release, I hope to add support for simple read/write to soundcard, to be able
to record and listen to data in numpy arrays.

2006-2007, David Cournapeau

LICENSE: audiolab is licensed under the LGPL, as is libsndfile itself. See
COPYING.txt for details.  """

from os.path import join
import os
import sys

DISTNAME            = 'scikits.audiolab'
DESCRIPTION         = 'A python module to make noise from numpy arrays'
LONG_DESCRIPTION    = descr
MAINTAINER          = 'David Cournapeau',
MAINTAINER_EMAIL    = 'david@ar.media.kyoto-u.ac.jp',
URL                 = 'http://www.ar.media.kyoto-u.ac.jp/members/david/softwares/audiolab',
LICENSE             = 'LGPL'
DOWNLOAD_URL        = URL

MAJOR = 0
MINOR = 9
MICRO = 0
DEV = True

CLASSIFIERS = ['Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Library or Lesser General '\
        'Public License (LGPL)', 'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Scientific/Engineering']

# The following is more or less random copy/paste from numpy.distutils ...
import setuptools

from distutils.errors import DistutilsError
from numpy.distutils.core import setup

def build_verstring():
    return '%d.%d.%d' % (MAJOR, MINOR, MICRO)

def build_fverstring():
    if DEV:
        return build_verstring() + 'dev'
    else:
        return build_verstring()

def write_version(fname):
    f = open(fname, "w")
    f.writelines("version = '%s'\n" % build_verstring())
    f.writelines("dev = %s\n" % DEV)
    f.writelines("full_version = %s\n" % build_fverstring())
    f.close()

def configuration(parent_package='',top_path=None, package_name=DISTNAME):
    if os.path.exists('MANIFEST'): os.remove('MANIFEST')

    write_version(os.path.join("scikits", "audiolab", "version.py"))
    write_version(os.path.join("scikits", "audiolab", "docs", "src",
                               "audiolab_version.py"))
    pkg_prefix_dir = os.path.join('scikits', 'audiolab')

    from numpy.distutils.misc_util import Configuration
    config = Configuration(None,parent_package,top_path,
        namespace_packages = ['scikits'],
        version     = build_fverstring(),
        maintainer  = MAINTAINER,
        maintainer_email = MAINTAINER_EMAIL,
        description = DESCRIPTION,
        license = LICENSE,
        url = URL,
        download_url = DOWNLOAD_URL,
        long_description = LONG_DESCRIPTION)

    config.set_options(
            ignore_setup_xxx_py=True,
            assume_default_configuration=True,
            delegate_options_to_subpackages=True,
            quiet=True,
            )

    # XXX: once in SVN, should add svn version...
    #print config.make_svn_version_py()

    config.add_subpackage('scikits')
    config.add_data_files('scikits/__init__.py')
    config.add_subpackage(DISTNAME)

    return config

if __name__ == "__main__":
    # setuptools version of config script
    setup(configuration=configuration,
          name=DISTNAME,
          install_requires='numpy',
          namespace_packages=['scikits'],
          packages=setuptools.find_packages(),
          include_package_data = True,
          test_suite="tester",
          zip_safe=True,
          classifiers=CLASSIFIERS)
