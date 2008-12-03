#! /usr/bin/env python
# Last Change: Wed Dec 03 07:00 PM 2008 J

from os.path import join

def configuration(parent_package='', top_path=None, package_name='soundio'):
    from numpy.distutils.misc_util import Configuration
    config = Configuration(package_name, parent_package, top_path)

    return config

if __name__ == "__main__":
    from numpy.distutils.core import setup
    #setup(**configuration(top_path='').todict())
    #setup(**configuration(top_path=''))
    setup(configuration=configuration)
