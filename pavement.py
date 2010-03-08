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
import paver.path
from paver.easy import options, Bunch, task, needs, dry, sh, call_task
from paver.setuputils import setup

import common

PDF_DESTDIR = paver.path.path('docs') / 'pdf'
HTML_DESTDIR = paver.path.path('docs') / 'html'

# Wine config for win32 builds
WINE_SITE_CFG = """\
[sndfile]
library_dirs = /home/david/.wine/drive_c/local/lib
include_dirs = /home/david/.wine/drive_c/local/include
libraries = sndfile,vorbis,vorbisenc,FLAC,ogg,wsock32
"""
WINE_PY25 = "/home/david/.wine/drive_c/Python25/python.exe"
WINE_PY26 = "/home/david/.wine/drive_c/Python26/python.exe"
WINE_PYS = {'2.6' : WINE_PY26, '2.5': WINE_PY25}

setup(name=common.DISTNAME,
        namespace_packages=['scikits'],
        packages=setuptools.find_packages(),
        install_requires=common.INSTALL_REQUIRE,
        version=common.VERSION,
        include_package_data=True)

options(sphinx=Bunch(builddir="build", sourcedir="src"),
        bootstrap=Bunch(bootstrap_dir="bootstrap"),
        virtualenv=Bunch(packages_to_install=["sphinx", "numpydoc"],
                         no_site_packages=False))

#----------------
# Bootstrap stuff
#----------------
@task
def bootstrap(options):
    """create virtualenv in ./bootstrap"""
    try:
        import virtualenv
    except ImportError, e:
        raise RuntimeError("virtualenv is needed for bootstrap")

    bdir = options.bootstrap_dir
    if not os.path.exists(bdir):
        os.makedirs(bdir)
    bscript = "boostrap.py"

    options.virtualenv.script_name = os.path.join(options.bootstrap_dir,
                                                  bscript)
    options.virtualenv.no_site_packages = True
    options.bootstrap.no_site_packages = True
    print options.virtualenv.script_name
    call_task('paver.virtual.bootstrap')
    sh('cd %s; %s %s' % (bdir, sys.executable, bscript))

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

VPYEXEC = "bootstrap/bin/python"

@task
def clean():
    """Remove build, dist, egg-info garbage."""
    d = ['build', 'dist', 'scikits.audiolab.egg-info', HTML_DESTDIR,
            PDF_DESTDIR]
    for i in d:
        paver.path.path(i).rmtree()

    (paver.path.path('docs') / options.sphinx.builddir).rmtree()

@task
def clean_bootstrap():
    paver.path.path('bootstrap').rmtree()

@task
@needs("setuptools.bdist_mpkg", "doc")
def dmg():
    pyver = ".".join([str(i) for i in sys.version_info[:2]])
    builddir = paver.path.path("build") / "dmg"
    builddir.rmtree()
    builddir.mkdir()

    # Copy mpkg into image source
    mpkg_n = mpkg_name()
    mpkg = paver.path.path("dist") / mpkg_n
    mpkg.copytree(builddir / mpkg_n)
    tmpkg = builddir / mpkg_n
    tmpkg.rename(builddir / ("audiolab-%s-py%s.mpkg" % (common.build_fverstring(), pyver)))

    # Copy docs into image source
    doc_root = paver.path.path(builddir) / "docs"
    html_docs = paver.path.path("docs") / "html"
    pdf_docs = paver.path.path("docs") / "pdf" / "audiolab.pdf"
    html_docs.copytree(doc_root / "html")
    pdf_docs.copy(doc_root / "audiolab.pdf")

    # Build the dmg
    image_name = "audiolab-%s.dmg" % common.build_fverstring()
    image = paver.path.path(image_name)
    image.remove()
    cmd = ["hdiutil", "create", image_name, "-srcdir", str(builddir)]
    sh(" ".join(cmd))
#options.setup.package_data =
#    setuputils.find_package_data("scikits/audiolab",
#                                 package="scikits/audiolab",
#                                 only_in_packages=False)

@task
def bdist_wininst_26():
    _bdist_wininst(pyver='2.6')

@task
def bdist_wininst_25():
    _bdist_wininst(pyver='2.5')

@task
@needs('bdist_wininst_25', 'bdist_wininst_26')
def bdist_wininst():
    pass

@task
@needs('clean', 'bdist_wininst')
def winbin():
    pass

def _bdist_wininst(pyver):
    site = paver.path.path('site.cfg')
    exists = site.exists()
    try:
        if exists:
            site.move('site.cfg.bak')
        a = open(str(site), 'w')
        a.writelines(WINE_SITE_CFG)
        a.close()
        sh('%s setup.py build -c mingw32 bdist_wininst' % WINE_PYS[pyver])
    finally:
        site.remove()
        if exists:
            paver.path.path('site.cfg.bak').move(site)

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
        """Build audiolab's documentation and install it into
        scikits/audiolab/docs"""
        paths = _latex_paths()
        sphinxopts = ['', '-b', 'latex', paths.srcdir, paths.latexdir]
        dry("sphinx-build %s" % (" ".join(sphinxopts),), sphinx.main, sphinxopts)

    @task
    @needs('latex')
    def pdf():
        paths = _latex_paths()
        def build_latex():
            subprocess.call(["make", "all-pdf"], cwd=paths.latexdir)
        dry("Build pdf doc", build_latex)
        PDF_DESTDIR.rmtree()
        PDF_DESTDIR.makedirs()
        pdf = paths.latexdir / "audiolab.pdf"
        pdf.copy(PDF_DESTDIR)

    @task
    @needs('build_version_files', 'paver.doctools.html')
    def html():
        """Build audiolab documentation and install it into docs"""
        builtdocs = paver.path.path("docs") / options.sphinx.builddir / "html"
        HTML_DESTDIR.rmtree()
        builtdocs.copytree(HTML_DESTDIR)

    @task
    @needs(['html', 'pdf'])
    def doc():
        pass

    @task
    def build_version_files(options):
        from common import write_version
        write_version(os.path.join("scikits", "audiolab", "version.py"))
        if os.path.exists(os.path.join("docs", "src")):
            write_version(os.path.join("docs", "src", "audiolab_version.py"))
    @task
    @needs('html', 'pdf', 'setuptools.command.sdist')
    def sdist(options):
        """Build tarball."""
        pass
