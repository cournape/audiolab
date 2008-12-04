# Last Change: Thu Dec 04 02:00 PM 2008 J
#
# This makefile is used to do all the "tricky things" before a release,
# including updating the doc, installing and testing the package, uploading the
# release to the website, etc...
#
# TODO: not fake dependencies....

PYVER		= 2.5
#PKG_VER		= $(shell python -c "from setup import build_fverstring; build_fverstring()")

BASEPATH	= $(PWD)
DATAPATH	= $(PWD)/scikits/audiolab/test_data/
DOCPATH		= $(PWD)/scikits/audiolab/docs/
EXAMPATH	= $(DOCPATH)/src/examples

SCIPYPATH	= /export/bbc8/local/lib/python$(PYVER)/site-packages
TMPPATH		= $(CURDIR)/../tmp

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

#=======================================================
# Code related to building audiolab in a tmp directory
#=======================================================
# Install the package in a tmp directory
$(TMPPATH): build_test

build_test:
	$(PYTHONRUN) setup.py install --prefix=$(TMPPATH) --single-version-externally-managed --record=/dev/null

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
	cd $(DATAPATH) && $(PYTHONRUN) $(EXAMPATH)/quick1.py
	@echo "---------- runing example usage1.py ----------";
	cd $(DATAPATH) && $(PYTHONRUN) $(EXAMPATH)/usage1.py
	@echo "---------- runing example usage2.py ----------";
	cd $(DATAPATH) && $(PYTHONRUN) $(EXAMPATH)/usage2.py
	@echo "---------- runing example format1.py ----------";
	cd $(DATAPATH) && $(PYTHONRUN) $(EXAMPATH)/format1.py
	@echo "---------- runing example format2.py ----------";
	cd $(DATAPATH) && $(PYTHONRUN) $(EXAMPATH)/format2.py
	@echo "---------- runing example write1.py ----------";
	cd $(DATAPATH) && $(PYTHONRUN) $(EXAMPATH)/write1.py
	@echo "---------- runing example matlab1.py ----------";
	cd $(DATAPATH) && $(PYTHONRUN) $(EXAMPATH)/matlab1.py

#=====================
# Code related to test
#=====================
tests: run_tests examples
	@echo "=================================="
	@echo " RELEASE $(PKG_VER) IS OK !"
	@echo "=================================="

# Run all tests
run_tests: $(TMPPATH)
	@echo "=============== running test ============"
	@cd $(TMPPATH) && PYTHONPATH=$(RUNPYTHONPATH) \
		nosetests -v -s \
		$(TMPPATH)/lib/python$(PYVER)/site-packages/scikits
	@echo "=============== Done ============"

#=====================
# Code related to doc
#=====================
doc:
	cd $(DOCPATH) && $(MAKE)

clean: clean_before_run
	cd $(DOCPATH) && $(MAKE) clean
