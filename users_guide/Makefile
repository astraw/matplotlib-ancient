# Makefile for matplotlib users_guide
PYTHON = /usr/local/bin/python2.3
# path to your matplotlib src tree
MATPLOTLIB = /home/jdhunter/python/projects/matplotlib

all:
	make graphs figs dvi pdf

clean: 	
	find . \( -name "*~" -o -name "*.pyc" -o -name "#*" \) | xargs rm -f;\
	rm -f *.log *.aux *.dvi *.bbl *.blg *.toc


pdf: 	
	latex users_guide
	bibtex users_guide
	pdflatex users_guide

dvi: 	
	latex users_guide
	bibtex users_guide
	latex users_guide

graphs:
	cd dot; ${PYTHON} makedot.py

figs:
	cd code; ${PYTHON} runall.py