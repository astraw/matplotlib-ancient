#!/usr/bin/env python

import os, sys

def clean():
    print 'cleaning...'
    os.system('rm -f *.bbl *.blg *.dvi *.log *.toc *.aux *.tex *.out *~ #*')
    os.system('rm -f examples/*~ examples/*.pyc')

for arg in sys.argv[1:]:
    if arg=='clean': clean()
    elif arg=='whatever': pass  # add your funcs here
    else: raise ValueError('Unrecognized command "%s"' % arg)
