#! /usr/bin/env python
# Last Change: Tue Jul 29 12:00 PM 2008 J

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

SNDFILE_MAJ_VERSION = 1

# The following is more or less random copy/paste from numpy.distutils ...
import setuptools
from distutils.errors import DistutilsError
from numpy.distutils.system_info import system_info, NotFoundError, dict_append, so_ext
from numpy.distutils.core import setup, Extension

class SndfileNotFoundError(NotFoundError):
    """ sndfile (http://www.mega-nerd.com/libsndfile/) library not found.
    Directories to search for the libraries can be specified in the
    site.cfg file (section [sndfile])."""

class sndfile_info(system_info):
    #variables to override
    section         = 'sndfile'
    notfounderror   = SndfileNotFoundError
    libname         = 'sndfile'
    header          = 'sndfile.h'

    def __init__(self):
        system_info.__init__(self)

    def library_extensions(self):
        # We rewrite library_extension
        exts = system_info.library_extensions(self)
        if sys.platform == 'win32':
            exts.insert(0, '.dll')
        return exts

    def calc_info(self):
        """ Compute the informations of the library """
        prefix  = 'lib'

        # Look for the shared library
        sndfile_libs    = self.get_libs('sndfile_libs', self.libname)
        lib_dirs        = self.get_lib_dirs()
        tmp             = None
        for i in lib_dirs:
            tmp = self.check_libs(i, sndfile_libs)
            if tmp is not None:
                info    = tmp
                break
        if tmp is None:
            raise SndfileNotFoundError("sndfile library not found")

        # Look for the header file
        include_dirs    = self.get_include_dirs()
        inc_dir         = None
        for d in include_dirs:
            p = self.combine_paths(d,self.header)
            if p:
                inc_dir     = os.path.dirname(p[0])
                headername  = os.path.abspath(p[0])
                break

        if inc_dir is None:
            raise SndfileNotFoundError("header not found")

        if inc_dir is not None and tmp is not None:
            if sys.platform == 'win32':
                # win32 case
                fullname    = prefix + tmp['libraries'][0] + \
                        '.dll'
            elif sys.platform == 'darwin':
                # Mac Os X case
                fullname    = prefix + tmp['libraries'][0] + '.' + \
                        str(SNDFILE_MAJ_VERSION) + '.dylib'
            else:
                # All others (Linux for sure; what about solaris) ?
                fullname    = prefix + tmp['libraries'][0] + '.so' + \
                        '.' + str(SNDFILE_MAJ_VERSION)
            fullname    = os.path.join(info['library_dirs'][0], fullname)
            dict_append(info, include_dirs=[inc_dir],
                    fullheadloc = headername,
                    fulllibloc  = fullname)
        else:
            raise RuntimeError("This is a bug")

        #print self
        self.set_info(**info)
        return

from header_parser import do_subst_in_file
def configuration(parent_package='',top_path=None, package_name=DISTNAME):
    if os.path.exists('MANIFEST'): os.remove('MANIFEST')
    if os.path.exists('scikits/audiolab/pysndfile.py'): os.remove('scikits/audiolab/pysndfile.py')

    pkg_prefix_dir = os.path.join('scikits', 'audiolab')
    # Check that sndfile can be found and get necessary informations
    # (assume only one header and one library file)
    sf_info     = sndfile_info()
    sf_config   = sf_info.get_info(2)
    headername  = sf_config['fullheadloc']
    libname     = sf_config['fulllibloc']

    # Now, generate pysndfile.py.in
    from generate_const import generate_enum_dicts
    repdict = generate_enum_dicts(headername)
    repdict['%SHARED_LOCATION%'] = libname
    #do_subst_in_file('pysndfile.py.in', 'pysndfile.py', repdict)
    do_subst_in_file(os.path.join(pkg_prefix_dir, 'pysndfile.py.in'),
            os.path.join(pkg_prefix_dir, 'pysndfile.py'),
            repdict)

    # Get the version
    from scikits.audiolab.info import VERSION as audiolab_version

    from numpy.distutils.misc_util import Configuration
    config = Configuration(package_name,parent_package,top_path,
        version     = audiolab_version,
        maintainer  = MAINTAINER,
        maintainer_email = MAINTAINER_EMAIL,
        description = DESCRIPTION,
        license = LICENSE,
        url = URL,
        download_url = DOWNLOAD_URL,
        long_description = LONG_DESCRIPTION)

    # XXX: once in SVN, should add svn version...
    #print config.make_svn_version_py()

    ## package_data does not work with sdist for setuptools 0.5 (setuptools bug),
    ## so we need to add them here while the bug is not solved...
    #config.add_data_files(('docs', \
    #        ['scikits/audiolab/docs/' + i for i in DOC_FILES]))

    config.add_data_files(('test_data', \
            ['scikits/audiolab/test_data/' + i
                for i in TEST_DATA_FILES]))

    config.add_data_files(('misc', \
            ['scikits/audiolab/misc/' + i
                for i in BAD_FLAC_FILES]))

    config.add_data_dir(('examples', 'scikits/audiolab/docs/examples'))

    return config

TEST_DATA_FILES = ['test.raw', 'test.flac', 'test.wav', 'test.au',
        'test.sdif']
#DOC_FILES = ['audiolab.pdf', 'index.txt']
BAD_FLAC_FILES = ['Makefile', 'badflac.flac', 'badflac.c']

if __name__ == "__main__":
    # setuptools version of config script

    # package_data does not work with sdist for setuptools 0.5 (setuptools bug)
    # So we cannot add data files via setuptools yet.

    #data_files = ['test_data/' + i for i in TEST_DATA_FILES]
    #data_files.extend(['docs/' + i for i in doc_files])

    setup(configuration = configuration,
        install_requires='numpy', # can also add version specifiers
        namespace_packages=['scikits'],
        packages=setuptools.find_packages(),
        include_package_data = True,
        #package_data = {'scikits.audiolab': data_files},
        test_suite="tester", # for python setup.py test
        zip_safe=True, # the package can run out of an .egg file
        #FIXME url, download_url, ext_modules
        classifiers =
            [ 'Development Status :: 4 - Beta',
              'Environment :: Console',
              'Intended Audience :: Developers',
              'Intended Audience :: Science/Research',
              'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
              'Topic :: Multimedia :: Sound/Audio',
              'Topic :: Scientific/Engineering']
    )
