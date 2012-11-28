import os
from distutils import log

from numpy.distutils.system_info import system_info, NotFoundError, dict_append, so_ext

def info_factory(name, libnames, headers, frameworks=None, 
                 section=None, classname=None):
    """Create a system_info class.

    Parameters
    ----------
        name : str
            name of the library
        libnames : seq
            list of libraries to look for
        headers : seq
            list of headers to look for
        classname : str
            name of the returned class
        section : str
            section name in the site.cfg

    Returns
    -------
        a system_info-derived class with the given meta-parameters
    """
    if not classname:
        classname = '%s_info' % name
    if not section:
        section = name
    if not frameworks:
        framesworks = []

    class _ret(system_info):
        def __init__(self):
            system_info.__init__(self)

        def library_extensions(self):
            return system_info.library_extensions(self)

        def calc_info(self):
            """ Compute the informations of the library """
            if libnames:
                libs = self.get_libs('libraries', '')
                if not libs:
                    libs = libnames
                # Look for the shared library
                lib_dirs = self.get_lib_dirs()
                tmp = None
                for d in lib_dirs:
                    tmp = self.check_libs(d, libs)
                    if tmp is not None:
                        info    = tmp
                        break
                if tmp is None:
                    return

                # Look for the header file
                include_dirs = self.get_include_dirs()
                inc_dir = None
                for d in include_dirs:
                    p = self.combine_paths(d, headers)
                    if p:
                        inc_dir = os.path.dirname(p[0])
                        dict_append(info, include_dirs=[d])
                        break

                if inc_dir is None:
                    log.info('  %s not found' % name)
                    return

                self.set_info(**info)
            else:
                # Look for frameworks
                if frameworks:
                    fargs = []
                    for f in frameworks:
                        p = "/System/Library/Frameworks/%s.framework" % f
                        if os.path.exists(p):
                            fargs.append("-framework")
                            fargs.append(f)
                    if fargs:
                        self.set_info(extra_link_args=fargs)
            return

    _ret.__name__ = classname
    _ret.section = section
    return _ret

