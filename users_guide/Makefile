# Makefile for matplotlib users_guide
PYTHON = /usr/local/bin/python2.3


clean: 	
	find . \( -name "*~" -o -name "*.pyc" -o -name "#*" \) | xargs rm -f;\
	rm -f *.log *.pdf *.aux *.dvi *.ps

pdf: 	
	pdflatex users_guide

dvi: 	
	latex users_guide
