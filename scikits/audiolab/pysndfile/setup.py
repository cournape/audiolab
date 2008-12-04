import os
import sys

from numpy.distutils.system_info import system_info, NotFoundError, dict_append, so_ext
from numpy.distutils.core import setup, Extension

from header_parser import do_subst_in_file

SNDFILE_MAJ_VERSION = 1

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

def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    confgr = Configuration('pysndfile',parent_package,top_path)

    if os.path.exists('pysndfile.py'):
        os.remove('pysndfile.py')

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

    pkg_dir = os.path.dirname(__file__)
    do_subst_in_file(os.path.join(pkg_dir, 'pysndfile.py.in'),
                     os.path.join(pkg_dir, 'pysndfile.py'), repdict)

    return confgr

if __name__ == "__main__":
    from numpy.distutils.core import setup
    setup(configuration=configuration)
