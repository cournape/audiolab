import os
from os.path import join

TEST_DATA_FILES = ['test.raw', 'test.flac', 'test.wav', 'test.au', 'test.sdif']
#BAD_FLAC_FILES = ['Makefile', 'badflac.flac', 'badflac.c']

def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration
    confgr = Configuration('audiolab',parent_package,top_path)
    confgr.add_subpackage('pysndfile')
    confgr.add_subpackage('soundio')

    confgr.add_data_files(('test_data',
                           [join('test_data', i) for i in TEST_DATA_FILES]))

    #config.add_data_files(('misc', \
    #        ['scikits/audiolab/misc/' + i
    #            for i in BAD_FLAC_FILES]))

    #confgr.add_data_dir(('examples', 'scikits/audiolab/docs/examples'))

    return confgr

if __name__ == "__main__":
    from numpy.distutils.core import setup
    config = configuration(top_path='').todict()
    setup(**config)
