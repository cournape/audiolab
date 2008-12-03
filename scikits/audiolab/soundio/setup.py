#! /usr/bin/env python
# Last Change: Wed Dec 03 08:00 PM 2008 J

from os.path import join
import os
import warnings

from numpy.distutils.system_info import system_info, NotFoundError, \
                                        dict_append, so_ext, get_info
class AlsaInfo(system_info):
    #variables to override
    section = 'alsa'
    libname = 'asound'
    header = 'alsa/asoundlib.h'

    def __init__(self):
        system_info.__init__(self)

    def library_extensions(self):
        # We rewrite library_extension
        exts = system_info.library_extensions(self)
        return exts

    def calc_info(self):
        """ Compute the informations of the library """
        prefix = 'lib'

        # Look for the shared library
        alsa_libs = self.get_libs('alsa_libs', self.libname)
        lib_dirs = self.get_lib_dirs()
        tmp = None
        for i in lib_dirs:
            tmp = self.check_libs(i, alsa_libs)
            if tmp is not None:
                info = tmp
                break
        if tmp is None:
            raise NotFoundError("alsa library (libasound) not found")

        # Look for the header file
        include_dirs = self.get_include_dirs()
        inc_dir = None
        for d in include_dirs:
            p = self.combine_paths(d,self.header)
            if p:
                inc_dir = os.path.dirname(p[0])
                headername = os.path.abspath(p[0])
                break

        if inc_dir is None:
            raise NotFoundError("Alsa header not found")

        if inc_dir is not None and tmp is not None:
            dict_append(info, include_dirs=[inc_dir])
        else:
            raise RuntimeError("This is a bug")

        #print self
        self.set_info(**info)
        return

def configuration(parent_package='', top_path=None, package_name='soundio'):
    from numpy.distutils.misc_util import Configuration
    config = Configuration(package_name, parent_package, top_path)

    alsa_info = AlsaInfo()
    try:
        alsa_config = alsa_info.get_info(0)
        config.add_extension("_alsa_backend", sources = ["alsa/_alsa_backend.c"],
                             extra_info=alsa_config)
    except NotFoundError:
        warnings.warn("Alsa not found - alsa backend not build")

    return config

if __name__ == "__main__":
    from numpy.distutils.core import setup
    #setup(**configuration(top_path='').todict())
    #setup(**configuration(top_path=''))
    setup(configuration=configuration)
