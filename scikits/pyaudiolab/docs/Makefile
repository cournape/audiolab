#pyfiles	= input/softwares/pyaudiolab/quick1.py \
#	input/softwares/pyaudiolab/usage1.py \
#	input/softwares/pyaudiolab/usage2.py \
#	input/softwares/pyaudiolab/format1.py \
#	input/softwares/pyaudiolab/format2.py \
#	input/softwares/pyaudiolab/write1.py \
#	input/softwares/pyaudiolab/matlab1.py
#
#pyaudiolab.tex: input/softwares/pyaudiolab/quick1.tex input/softwares/pyaudiolab/quick1.tex
#
#all: input/softwares/pyaudiolab/quick1.tex
#
py2tex	= PYTHONPATH=/home/david/local/lib/python2.4/site-packages pygmentize -l python -f tex
rst2tex	= PYTHONPATH=/home/david/local/lib/python2.4/site-packages rst2newlatex.py \
		  --stylesheet-path base.tex --user-stylesheet user.tex 

pytexfiles	= pyaudiolab.tex quick1.tex \
			  usage1.tex \
			  usage2.tex \
			  format1.tex \
			  format2.tex \
			  write1.tex \
			  matlab1.tex 

SOURCEPATH	= $(PWD)

EXTTOCLEAN=.chk .dvi .log .aux .bbl .blg .blig .ilg .toc .lof .lot .idx .ind .out .bak .ps .pdf .bm

pyaudiolab.pdf: $(pytexfiles)
	pdflatex $<
	pdflatex $<
	pdflatex $<

pyaudiolab.tex: index.txt
	$(rst2tex) $< > $@

quick1.tex: examples/quick1.py
	$(py2tex) $< > $@

usage1.tex: examples/usage1.py
	$(py2tex) $< > $@

usage2.tex: examples/usage2.py
	$(py2tex) $< > $@

format1.tex: examples/format1.py
	$(py2tex) $< > $@

format2.tex: examples/format2.py
	$(py2tex) $< > $@

write1.tex: examples/write1.py
	$(py2tex) $< > $@

matlab1.tex: examples/matlab1.py
	$(py2tex) $< > $@

clean:
	for i in $(pytexfiles); do \
		rm -f `echo $$i`; \
	done;
	for i in $(SOURCEPATH); do \
		for j in $(EXTTOCLEAN); do \
			rm -f  `echo $$i/*$$j`; \
		done; \
	done;
