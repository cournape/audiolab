from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from numpy.distutils.misc_util import get_numpy_include_dirs

setup(name = "PyrexGuide",
      ext_modules=[ 
          Extension("_alsa", ["_alsa.pyx"], 
                    libraries = ['asound'], 
                    include_dirs = get_numpy_include_dirs())],
      cmdclass = {'build_ext': build_ext})

