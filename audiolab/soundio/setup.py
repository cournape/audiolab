#! /usr/bin/env python
# Last Change: Mon Dec 08 03:00 PM 2008 J

from os.path import join
import os
import warnings

from setuphelp import info_factory, NotFoundError

def configuration(parent_package='', top_path=None, package_name='soundio'):
    from numpy.distutils.misc_util import Configuration
    config = Configuration(package_name, parent_package, top_path)

    alsa_info = info_factory('alsa', ['asound'], ['alsa/asoundlib.h'],
                             classname='AlsaInfo')()
    try:
        alsa_config = alsa_info.get_info(2)
        config.add_extension("_alsa_backend", sources = ["alsa/_alsa_backend.c"],
                             extra_info=alsa_config)
    except NotFoundError:
        warnings.warn("Alsa not found - alsa backend not build")

    core_audio_info = info_factory('CoreAudio', [], [],
                             frameworks=["CoreAudio"],
                             classname='CoreAudioInfo')()
    try:
        core_audio_config = core_audio_info.get_info(2)
        config.add_extension("macosx_backend", sources=["macosx/macosx_backend.c"],
                             extra_info=core_audio_config)
    except NotFoundError:
        warnings.warn("CoreAudio not found - CoreAudio backend not build")

    return config

if __name__ == "__main__":
    from numpy.distutils.core import setup
    #setup(**configuration(top_path='').todict())
    #setup(**configuration(top_path=''))
    setup(configuration=configuration)
