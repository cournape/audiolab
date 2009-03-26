import os
import subprocess
import sys
import shutil

import sphinx

import setuptools
import distutils
import numpy.distutils

try:
    from paver.tasks import VERSION as _PVER
    if not _PVER >= '1.0':
        raise RuntimeError("paver version >= 1.0 required (was %s)" % _PVER)
except ImportError, e:
    raise RuntimeError("paver version >= 1.0 required")

import paver
import paver.doctools
from paver.easy import Bunch, options, task, needs, dry, sh
from paver.setuputils import setup

import common

setup(
    name=common.DISTNAME,
    namespace_packages=['scikits'],
    packages=setuptools.find_packages(),
    install_requires=common.INSTALL_REQUIRE,
    version=common.VERSION,
    include_package_data=True,
)

options(
        sphinx=Bunch(builddir="build", sourcedir="src"),
        virtualenv=Bunch(script_name="install/bootstrap.py")
)

def macosx_version():
    st = subprocess.Popen(["sw_vers"], stdout=subprocess.PIPE)
    out = st.stdout.readlines()
    import re
    ver = re.compile("ProductVersion:\s+([0-9]+)\.([0-9]+)\.([0-9]+)")
    for i in out:
        m = ver.match(i)
        if m:
            return m.groups()

def mpkg_name():
    maj, min = macosx_version()[:2]
    pyver = ".".join([str(i) for i in sys.version_info[:2]])
    return "scikits.audiolab-%s-py%s-macosx%s.%s.mpkg" % (common.build_fverstring(),
                            pyver, maj, min)

VPYEXEC = "install/bin/python"

@task
@needs('paver.virtual.bootstrap')
def bootstrap():
    """create virtualenv in ./install"""
    # XXX: fix the mkdir
    sh('mkdir -p install')
    sh('cd install; %s bootstrap.py' % sys.executable)

@task
@needs('bootstrap')
def test_install():
    """Install the package into the venv."""
    sh('%s setup.py install' % VPYEXEC)

@task
def build_version_files(options):
    from common import write_version
    write_version(os.path.join("scikits", "audiolab", "version.py"))
    if os.path.exists(os.path.join("docs", "src")):
        write_version(os.path.join("docs", "src", "audiolab_version.py"))

@task
#@needs(['latex', 'html'])
def dmg():
    builddir = path("build") / "dmg"
    builddir.rmtree()
    builddir.mkdir()

    # Copy mpkg into image source
    mpkg_n = mpkg_name()
    mpkg = path("dist") / mpkg_n
    mpkg.copytree(builddir / mpkg_n)

    # Copy docs into image source
    doc_root = path(builddir) / "docs"
    html_docs = path("docs") / "html"
    pdf_docs = path("docs") / "pdf" / "audiolab.pdf"
    html_docs.copytree(doc_root / "html")
    pdf_docs.copy(doc_root / "audiolab.pdf")

    # Build the dmg
    image_name = "audiolab-%s.dmg" % common.build_fverstring()
    image = path(image_name)
    image.remove()
    cmd = ["hdiutil", "create", image_name, "-srcdir", str(builddir)]
    subprocess.Popen(cmd)
#options.setup.package_data =
#    setuputils.find_package_data("scikits/audiolab",
#                                 package="scikits/audiolab",
#                                 only_in_packages=False)

if paver.doctools.has_sphinx:
    def _latex_paths():
        """look up the options that determine where all of the files are."""
        opts = options
        docroot = paver.path.path(opts.get('docroot', 'docs'))
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
    @needs('build_version_files')
    def latex():
        """Build Audiolab's documentation and install it into
        scikits/audiolab/docs"""
        paths = _latex_paths()
        sphinxopts = ['', '-b', 'latex', paths.srcdir, paths.latexdir]
        dry("sphinx-build %s" % (" ".join(sphinxopts),), sphinx.main, sphinxopts)
        def build_latex():
            subprocess.call(["make", "all-pdf"], cwd=paths.latexdir)
        dry("Build pdf doc", build_latex)
        destdir = paver.path.path("docs") / "pdf"
        destdir.rmtree()
        destdir.makedirs()
        pdf = paths.latexdir / "audiolab.pdf"
        pdf.move(destdir)

    @task
    @needs('build_version_files', 'paver.doctools.html')
    def html_build():
        """Build Audiolab's html documentation."""
        pass

    @task
    @needs(['html_build'])
    def html():
        """Build Audiolab's documentation and install it into
        scikits/audiolab/docs"""
        builtdocs = paver.path.path("docs") / options.sphinx.builddir / "html"
        destdir = paver.path.path("docs") / "html"
        destdir.rmtree()
        builtdocs.move(destdir)

    @task
    @needs(['html', 'latex'])
    def doc():
        pass

    @task
    @needs('setuptools.command.sdist')
    def sdist(options):
        """Build tarball."""
        pass

    @task
    @needs(['doc', 'pavement.sdist'])
    def release_sdist(options):
        """Build doc + tarball."""
        pass
