# Last Change: Tue Jul 17 11:00 AM 2007 J
#
# This makefile is used to do all the "tricky things" before a release,
# including updating the doc, installing and testing the package, uploading the
# release to the website, etc...
#
# TODO: not fake dependencies....

PKG_VER 	= $(shell cat scikits/audiolab/info.py | grep __version__ | tr -s " " | cut -f 3 -d" " \
			  | cut -f 2 -d\')

BASEPATH	= $(PWD)
DATAPATH	= $(PWD)/scikits/audiolab/test_data/
DOCPATH		= $(PWD)/scikits/audiolab/docs/
EXAMPATH	= $(DOCPATH)/examples

SCIPYPATH	= $(HOME)/local/lib/python2.5/site-packages
TMPPATH		= $(CURDIR)/../tmp

PYTHONCMD	= PYTHONPATH=$(TMPPATH)/lib/python2.5/site-packages:$(SCIPYPATH) python -c 
PYTHONRUN	= PYTHONPATH=$(TMPPATH)/lib/python2.5/site-packages:$(SCIPYPATH) python 

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
	$(PYTHONRUN) setup.py install --prefix=$(TMPPATH)

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
	cd .. && $(PYTHONCMD) "import scikits.audiolab as audiolab; print audiolab; audiolab.test()"
	@echo "=============== Done ============"

#=====================
# Code related to doc
#=====================
doc:
	cd $(DOCPATH) && $(MAKE)

clean: clean_before_run
	cd $(DOCPATH) && $(MAKE) clean
