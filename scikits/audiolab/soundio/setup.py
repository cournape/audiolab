from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(name = "PyrexGuide",
      ext_modules=[Extension("_alsa", ["_alsa.pyx"], libraries = ['asound'])],
      cmdclass = {'build_ext': build_ext})

