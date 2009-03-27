#! /usr/bin/env python
# Last Change: Fri Mar 27 05:00 PM 2009 J

# Copyright (C) 2006-2007 Cournapeau David <cournape@gmail.com>
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option) any
# later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this library; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

# TODO:
#   - check how to handle cmd line build options with distutils and use
#   it in the building process

from os.path import join
import os
import sys

# The following is more or less random copy/paste from numpy.distutils ...
import setuptools

from distutils.errors import DistutilsError
from numpy.distutils.core import setup

from common import *

def configuration(parent_package='',top_path=None, package_name=DISTNAME):
    if os.path.exists('MANIFEST'): os.remove('MANIFEST')

    write_info(os.path.join("scikits", "audiolab", "info.py"))
    write_version(os.path.join("scikits", "audiolab", "version.py"))
    # XXX: find a way to include the doc in sdist
    if os.path.exists(os.path.join("docs", "src")):
        write_version(os.path.join("docs", "src", "audiolab_version.py"))
    pkg_prefix_dir = os.path.join('scikits', 'audiolab')

    from numpy.distutils.misc_util import Configuration
    config = Configuration(None,parent_package,top_path,
        namespace_packages = ['scikits'],
        version     = build_fverstring(),
        maintainer  = MAINTAINER,
        maintainer_email = MAINTAINER_EMAIL,
        description = DESCRIPTION,
        license = LICENSE,
        url = URL,
        download_url = DOWNLOAD_URL,
        long_description = LONG_DESCRIPTION)

    config.set_options(
            ignore_setup_xxx_py=True,
            assume_default_configuration=True,
            delegate_options_to_subpackages=True,
            quiet=True,
            )

    # XXX: once in SVN, should add svn version...
    #print config.make_svn_version_py()

    config.add_subpackage('scikits')
    config.add_data_files('scikits/__init__.py')

    config.add_subpackage(DISTNAME)

    return config

if __name__ == "__main__":
    # setuptools version of config script
    setup(configuration=configuration,
          name=DISTNAME,
          install_requires=INSTALL_REQUIRE,
          namespace_packages=['scikits'],
          packages=setuptools.find_packages(),
          include_package_data = True,
          test_suite="tester",
          zip_safe=False,
          classifiers=CLASSIFIERS)
