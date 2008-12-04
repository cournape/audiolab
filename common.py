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
        return build_verstring() + 'dev'
    else:
        return build_verstring()

def write_version(fname):
    f = open(fname, "w")
    f.writelines("version = '%s'\n" % build_verstring())
    f.writelines("dev =%s\n" % DEV)
    f.writelines("full_version = '%s'\n" % build_fverstring())
    f.close()

VERSION = build_fverstring()
INSTALL_REQUIRE = 'numpy'
