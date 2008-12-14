import os
from tempfile import mkstemp
import sys

import scikits.audiolab

TEST_DATA_DIR = os.path.join(os.path.dirname(scikits.audiolab.__file__),
                             'test_data')

def open_tmp_file(name):
    """On any sane platforms, return a fd on a tmp file. On windows, returns
    the filename, and as such, is not secure (someone else can reopen the file
    in between)."""
    fd, cfilename = mkstemp(name)
    if sys.platform == 'win32':
        return fd, cfilename, cfilename
    else:
        return fd, fd, cfilename

def close_tmp_file(fd, filename):
    """On any sane platforms, remove the file . On windows, only close the
    file."""
    os.close(fd)
    os.remove(filename)
