import os
import sys

from numpy.distutils.core import setup, Extension
from setuphelp import info_factory, NotFoundError

SNDFILE_MAJ_VERSION = 1

def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    confgr = Configuration('pysndfile',parent_package,top_path)

    if os.path.exists('pysndfile.py'):
        os.remove('pysndfile.py')

    # Check that sndfile can be found and get necessary informations
    sf_info = info_factory('sndfile', ['sndfile'], ['sndfile.h'],
                           classname='SndfileInfo')()
    try:
        sf_config = sf_info.get_info(2)
    except NotFoundError:
        raise NotFoundError("""\
sndfile (http://www.mega-nerd.com/libsndfile/) library not found.
Directories to search for the libraries can be specified in the
site.cfg file, in section [sndfile].""")

    confgr.add_extension('_sndfile', ['_sndfile.c'], extra_info=sf_config)

    return confgr

if __name__ == "__main__":
    from numpy.distutils.core import setup
    setup(configuration=configuration)
