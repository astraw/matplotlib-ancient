#!/usr/bin/env python

import os, sys

def clean():
    print 'cleaning...'
    os.system('rm -f *.bbl *.blg *.dvi *.log *.toc *.aux *.tex *.out *~ #*')
    os.system('rm -f examples/*~ examples/*.pyc')

def pdf():
    print 'making pdf'
    #os.system('lyx -e pdf main.lyx')
    os.system('./lyxport2 --pdf main')

def ps():
    print 'making ps'
    #os.system('lyx -e pdf main.lyx')
    os.system('./lyxport2 --ps main')

def dist():
    pdf()
    try:
        os.symlink('main.pdf','practical_scicomp_py.pdf')
    except OSError:
        pass
    
for arg in sys.argv[1:]:
    try:
        exec arg
    except NameError:
        raise NameError('Unrecognized command "%s"' % arg)
    else:
        exec arg+'()'
