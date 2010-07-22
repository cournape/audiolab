descr   = """\
Audiolab is a python package for audio file IO using numpy arrays. It supports
many different audio formats, including wav, aiff, au, flac, ogg, htk. It also
supports output to audio device (Mac OS X and Linux only).

For simplicity, a matlab-like API is provided for simple import/export; a more
complete API is also available.

Audiolab is essentially a wrapper around Erik de Castro Lopo's excellent
libsndfile:

http://www.mega-nerd.com/libsndfile/

LICENSE: audiolab is licensed under the LGPL, as is libsndfile itself. See
COPYING.txt for details.  

2006-2008, David Cournapeau
"""

DISTNAME            = 'scikits.audiolab'
DESCRIPTION         = 'A python module to make noise from numpy arrays'
LONG_DESCRIPTION    = descr
MAINTAINER          = 'David Cournapeau'
MAINTAINER_EMAIL    = 'cournape@gmail.com'
URL                 = 'http://cournape.github.com/audiolab'
LICENSE             = 'LGPL'
DOWNLOAD_URL        = URL

MAJOR = 0
MINOR = 11
MICRO = 0
DEV = False

CLASSIFIERS = ['Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Library or Lesser General '\
        'Public License (LGPL)', 'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Scientific/Engineering']

def build_verstring():
    return '%d.%d.%d' % (MAJOR, MINOR, MICRO)

def build_fverstring():
    if DEV:
        return build_verstring() + '.dev'
    else:
        return build_verstring()

def write_version(fname):
    f = open(fname, "w")
    f.write("""
short_version='%s'
version=short_version
dev=%s
if dev:
    version += '.dev'
""" % (build_verstring(), DEV))
    f.close()

def write_info(fname):
    f = open(fname, "w")
    f.writelines("# THIS FILE IS GENERATED FROM THE SETUP.PY. DO NOT EDIT.\n")
    f.writelines('"""%s"""' % descr)
    f.writelines("""
# version of the python module (compatibility -> use
# scikits.samplerate.version.version instead, to be consistent with numpy)
from version import short_version as version
ignore  = False""")
    f.close()

VERSION = build_fverstring()
INSTALL_REQUIRE = 'numpy'
