#!/usr/bin/env python

import os, sys

def clean():
    print 'cleaning...'
    os.system('rm -f *.bbl *.blg *.dvi *.log *.toc *.aux *.tex *.out *~ #*')
    os.system('rm -f examples/*~ examples/*.pyc')

def pdf():
    print 'making pdf'
    os.system('lyx -e pdf main.lyx')
    
for arg in sys.argv[1:]:
    if arg=='clean': clean()
    elif arg=='pdf': pdf()  
    else: raise ValueError('Unrecognized command "%s"' % arg)
