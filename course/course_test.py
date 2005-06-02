#!/usr/bin/env python
"""Minimal test script to check for modules needed in python course"""

modules = ['scipy','weave','matplotlib','IPython','mayavi','pyvtk']

for mname in modules:
    try:
        exec "import %s" % mname
    except ImportError:
        print '*** ERROR: module %s could not be imported.' % mname
    else:
        print '%s: OK' % mname
