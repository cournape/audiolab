#! /bin/sh
# Last Change: Fri May 25 10:00 AM 2007 J
EPYDOCOPTS="--latex -v --no-private --exclude test_*"
PYTHONPATH=/home/david/local/lib/python2.5/site-packages/ /home/david/local/bin/epydoc $EPYDOCOPTS scikits/pyaudiolab/
