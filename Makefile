# Last Change: Tue Jul 17 11:00 AM 2007 J
#
# This makefile is used to do all the "tricky things" before a release,
# including updating the doc, installing and testing the package, uploading the
# release to the website, etc...
#
# TODO: not fake dependencies....

PKG_VER 	= $(shell cat scikits/pyaudiolab/info.py | grep __version__ | tr -s " " | cut -f 3 -d" " \
			  | cut -f 2 -d\')

BASEPATH	= $(PWD)
DATAPATH	= $(PWD)/scikits/pyaudiolab/test_data/
DOCPATH		= $(PWD)/scikits/pyaudiolab/docs/
EXAMPATH	= $(DOCPATH)/examples

SCIPYPATH	= $(HOME)/local/lib/python2.5/site-packages
TMPPATH		= $(CURDIR)/../tmp

PYTHONCMD	= PYTHONPATH=$(TMPPATH)/lib/python2.5/site-packages:$(SCIPYPATH) python -c 
PYTHONRUN	= PYTHONPATH=$(TMPPATH)/lib/python2.5/site-packages:$(SCIPYPATH) python 

RELEASELOC	= $(WWWHOMEDIR)/archives/pyaudiolab/releases

do_release: clean src examples tests

release: do_release upload_release

upload_release:  dist/pyaudiolab-$(PKG_VER).tar.gz \
	dist/pyaudiolab-$(PKG_VER).tar.bz2 \
	dist/pyaudiolab-$(PKG_VER).zip 
	@echo "Uploading version $(PKG_VER) ..."
	@read n
	rcp dist/pyaudiolab-$(PKG_VER).tar.gz $(RELEASELOC)
	rcp dist/pyaudiolab-$(PKG_VER).tar.bz2 $(RELEASELOC)
	rcp dist/pyaudiolab-$(PKG_VER).zip $(RELEASELOC)

src: build_src

build_src: dist/pyaudiolab-$(PKG_VER).tar.gz \
	dist/pyaudiolab-$(PKG_VER).tar.bz2 \
	dist/pyaudiolab-$(PKG_VER).zip 

dist/pyaudiolab-$(PKG_VER).tar.gz: doc
		python setup.py sdist --format=gztar

dist/pyaudiolab-$(PKG_VER).zip: doc
		python setup.py sdist --format=zip

dist/pyaudiolab-$(PKG_VER).tar.bz2: doc
		python setup.py sdist --format=bztar

#=======================================================
# Code related to building pyaudiolab in a tmp directory
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
	$(PYTHONCMD) "import scikits.pyaudiolab as pyaudiolab; print pyaudiolab; pyaudiolab.test()"
	@echo "=============== Done ============"

#=====================
# Code related to doc
#=====================
doc:
	cd $(DOCPATH) && $(MAKE)
## Commands For doc
#PY2TEX	= PYTHONPATH=/home/david/local/lib/python2.4/site-packages pygmentize -l \
#		  python -f tex
#RST2TEX	= PYTHONPATH=/home/david/local/lib/python2.4/site-packages rst2newlatex.py \
#		  --stylesheet-path base.tex --user-stylesheet user.tex 


#PYTEXFILES	= pyaudiolab.tex quick1.tex \
#			  usage1.tex \
#			  usage2.tex \
#			  format1.tex \
#			  format2.tex \
#			  write1.tex \
#			  matlab1.tex 
#
#DOCDIR	= docs
#
#build_tex: 
#EXTTOCLEAN=.chk .dvi .log .aux .bbl .blg .blig .ilg .toc .lof .lot .idx .ind .out .bak .ps .pdf .bm
#
#clean_tex: 
#	for i in $(PYTEXFILES); do \
#		rm -f `echo $(DOCDIR)/$$i`; \
#	done;
#	for i in $(DOCDIR); do \
#		for j in $(EXTTOCLEAN); do \
#			rm -f  `echo $$i/*$$j`; \
#		done; \
#	done;
#
#clean_doc: clean_tex

clean: clean_before_run
	cd $(DOCPATH) && $(MAKE) clean
