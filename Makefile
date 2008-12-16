# Last Change: Sun Dec 14 08:00 PM 2008 J
#
# This makefile is used to do all the "tricky things" before a release,
# including updating the doc, installing and testing the package, uploading the
# release to the website, etc...
#
# TODO: not fake dependencies....

PYVER		= 2.5
PKG_VER		= 0.10.0

BASEPATH	= $(PWD)
DATAPATH	= $(PWD)/scikits/audiolab/test_data/
DOCPATH		= $(PWD)/docs/
EXAMPATH	= $(DOCPATH)/src/examples

SCIPYPATH	= /export/bbc8/local/lib/python$(PYVER)/site-packages
TMPPATH		= $(PWD)/tmp

PYTHONCMD	= PYTHONPATH=$(TMPPATH)/lib/python$(PYVER)/site-packages:$(PYTHONPATH) python -c
PYTHONRUN	= PYTHONPATH=$(TMPPATH)/lib/python$(PYVER)/site-packages:$(PYTHONPATH) python

RUNPYTHONPATH	= $(TMPPATH)/lib/python$(PYVER)/site-packages:$(PYTHONPATH)

RELEASELOC	= $(WWWHOMEDIR)/archives/audiolab/releases

do_release: clean src examples tests

release: do_release upload_release

upload_release:  dist/audiolab-$(PKG_VER).tar.gz \
	dist/audiolab-$(PKG_VER).tar.bz2 \
	dist/audiolab-$(PKG_VER).zip
	@echo "Uploading version $(PKG_VER) ..."
	@read n
	rcp dist/audiolab-$(PKG_VER).tar.gz $(RELEASELOC)
	rcp dist/audiolab-$(PKG_VER).tar.bz2 $(RELEASELOC)
	rcp dist/audiolab-$(PKG_VER).zip $(RELEASELOC)

src: build_src

build_src: dist/audiolab-$(PKG_VER).tar.gz \
	dist/audiolab-$(PKG_VER).tar.bz2 \
	dist/audiolab-$(PKG_VER).zip

dist/audiolab-$(PKG_VER).tar.gz: doc
		python setup.py sdist --format=gztar

dist/audiolab-$(PKG_VER).zip: doc
		python setup.py sdist --format=zip

dist/audiolab-$(PKG_VER).tar.bz2: doc
		python setup.py sdist --format=bztar

#=====================================
# Building audiolab in a tmp directory
#=====================================
build_sdist:
	paver sdist

$(TMPPATH):
	mkdir -p $(TMPPATH)

extract_sdist: $(TMPPATH) build_sdist
	cp dist/scikits.audiolab-$(PKG_VER).tar.gz $(TMPPATH)
	(cd $(TMPPATH) && tar -xzf scikits.audiolab-$(PKG_VER).tar.gz)

build_test: extract_sdist
	(cd $(TMPPATH)/scikits.audiolab-$(PKG_VER) && $(PYTHONRUN) setup.py \
		install --prefix=$(TMPPATH) \
		--single-version-externally-managed --record=/dev/null)

# Clean the tmp dir
clean_before_run:
	rm -rf $(TMPPATH)

#===========================
# Code related to examples
#===========================
examples: run_examples

# Run examples in docs/examples
run_examples:  $(TMPPATH)
	#for i in $(BASEPATH)/docs/examples/*.py; do\
	#	echo "========== runing example $$i ==========";\
	#	$(PYTHONRUN) $$i; \
	#done;
	# Why when using the above loop, Make does not stop when one script fails ?
	@echo "---------- runing example quick1.py ----------";
	cd $(DATAPATH) && $(PYTHONRUN) $(EXAMPATH)/obsolete/quick1.py
	@echo "---------- runing example usage1.py ----------";
	cd $(DATAPATH) && $(PYTHONRUN) $(EXAMPATH)/obsolete/usage1.py
	@echo "---------- runing example usage2.py ----------";
	cd $(DATAPATH) && $(PYTHONRUN) $(EXAMPATH)/obsolete/usage2.py
	@echo "---------- runing example format1.py ----------";
	cd $(DATAPATH) && $(PYTHONRUN) $(EXAMPATH)/obsolete/format1.py
	@echo "---------- runing example write1.py ----------";
	cd $(DATAPATH) && $(PYTHONRUN) $(EXAMPATH)/obsolete/write1.py
	@echo "---------- runing example matlab1.py ----------";
	cd $(DATAPATH) && $(PYTHONRUN) $(EXAMPATH)/matlab1.py
	@echo "---------- runing example play.py ----------";
	cd $(DATAPATH) && $(PYTHONRUN) $(EXAMPATH)/play.py
	@echo "---------- runing example over1.py ----------";
	cd $(DATAPATH) && $(PYTHONRUN) $(EXAMPATH)/over1.py
	@echo "---------- runing example over2.py ----------";
	cd $(DATAPATH) && $(PYTHONRUN) $(EXAMPATH)/over2.py
	@echo "---------- runing example over3.py ----------";
	cd $(DATAPATH) && $(PYTHONRUN) $(EXAMPATH)/over3.py

#=====================
# Code related to test
#=====================
tests: run_tests examples
	@echo "=================================="
	@echo " RELEASE $(PKG_VER) IS OK !"
	@echo "=================================="

# Run all tests
run_tests: build_test
	@echo "=============== running test ============"
	@cd $(TMPPATH) && PYTHONPATH=$(RUNPYTHONPATH) \
		nosetests -v -s \
		$(TMPPATH)/lib/python$(PYVER)/site-packages/scikits/audiolab
	@echo "=============== Done ============"

#=====================
# Code related to doc
#=====================
doc:
	cd $(DOCPATH) && $(MAKE)

clean: clean_before_run
	cd $(DOCPATH) && $(MAKE) clean
	rm -rf $(TMPPATH)
	rm -rf build
	rm -rf dist
