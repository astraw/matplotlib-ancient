# Makefile for matplotlib users_guide
PYTHON = /usr/local/bin/python2.3

all:
	make figs dvi pdf

clean: 	
	find . \( -name "*~" -o -name "*.pyc" -o -name "#*" \) | xargs rm -f;\
	rm -f *.log *.pdf *.aux *.dvi *.ps *.bbl *.blg *.toc


pdf: 	
	pdflatex users_guide

dvi: 	
	latex users_guide

figs:
	cd code; ${PYTHON} runall.py