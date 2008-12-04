import os
import subprocess

import sphinx

import setuptools
import numpy.distutils

import paver
import paver.doctools

import common
from setup import configuration

options(
        setup=Bunch(
            name=common.DISTNAME,
            namespace_packages=['scikits'],
            packages=setuptools.find_packages(),
            install_requires=common.INSTALL_REQUIRE,
            version=common.VERSION,
            include_package_data=True,
            ),
        sphinx=Bunch(
            builddir="build",
            sourcedir="src"
            ),

        )

#options.setup.package_data = 
#    setuputils.find_package_data("scikits/audiolab", 
#                                 package="scikits/audiolab",
#                                 only_in_packages=False)

if paver.doctools.has_sphinx:
    def _latex_paths():
        """look up the options that determine where all of the files are."""
        opts = options
        docroot = path(opts.get('docroot', 'docs'))
        if not docroot.exists():
            raise BuildFailure("Sphinx documentation root (%s) does not exist."
                    % docroot)
        builddir = docroot / opts.get("builddir", ".build")
        builddir.mkdir()
        srcdir = docroot / opts.get("sourcedir", "")
        if not srcdir.exists():
            raise BuildFailure("Sphinx source file dir (%s) does not exist" 
                    % srcdir)
        latexdir = builddir / "latex"
        latexdir.mkdir()
        return Bunch(locals())

    @task
    def latex():
        """Build Audiolab's documentation and install it into
        scikits/audiolab/docs"""
        paths = _latex_paths()
        sphinxopts = ['', '-b', 'latex', paths.srcdir, paths.latexdir]
        dry("sphinx-build %s" % (" ".join(sphinxopts),), sphinx.main, sphinxopts)
        def build_latex():
            subprocess.call(["make", "all-pdf"], cwd=paths.latexdir)
        dry("Build pdf doc", build_latex)
        destdir = path("scikits") / "audiolab" / "docs" / "pdf"
        destdir.rmtree()
        destdir.makedirs()
        pdf = paths.latexdir / "audiolab.pdf"
        pdf.move(destdir)

    @task
    @needs(['paver.doctools.html'])
    def html():
        """Build Audiolab's documentation and install it into
        scikits/audiolab/docs"""
        builtdocs = path("docs") / options.sphinx.builddir / "html"
        destdir = path("scikits") / "audiolab" / "docs" / "html"
        destdir.rmtree()
        builtdocs.move(destdir)

    @task
    @needs(['html', 'latex'])
    def doc():
        pass

    @task
    @needs(['doc', 'setuptools.command.sdist'])
    def sdist():
        """Build doc + tarball."""
        pass
