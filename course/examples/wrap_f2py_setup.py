#!/usr/bin/env python
"""Setup script for F2PY-processed, Fortran based extension modules.

A typical call is:

% ./setup.py install --home=~/usr

This will build and install the generated modules in ~/usr/lib/python.

If called with no args, the script defaults to the above call form (it
automatically adds the 'install --home=~/usr' options)."""

# Global variables for this extension:
name         = "mwadap_tools"  # name of the generated python extension (.so)
description  = "F2PY-wrapped MultiWavelet Tree Toolbox"
author       = "Fast Algorithms Group - CU Boulder"
author_email = "fperez@colorado.edu"

# Necessary sources, _including_ the .pyf interface file
sources = """
binary_decomp.f90 binexpandx.f90 bitsequence.f90 constructwv.f90
display_matrix.f90 findkeypos.f90 findlevel.f90 findnodx.f90 gauleg.f90
gauleg2.f90 gauleg3.f90 ihpsort.f90 invert_f2cmatrix.f90 keysequence2d.f90
level_of_nsi.f90 matmult.f90 plegnv.f90 plegvec.f90 r2norm.f90 xykeys.f90

mwadap_tools.pyf""".split()

# Additional libraries required by our extension module (these will be linked
# in with -l):
libraries = ['m']

# Set to true (1) to turn on Fortran/C API debugging (very verbose)
debug_capi = 0

#***************************************************************************
# Do not modify the code below unless you know what you are doing.

# Required modules
import sys,os
from os.path import expanduser,expandvars
from scipy_distutils.core import setup,Extension

expand_sh = lambda path: expanduser(expandvars(path))

# Additional directories for libraries (besides the compiler's defaults)
fc_vendor = os.environ.get('FC_VENDOR','Gnu').lower()
library_dirs = ["~/usr/lib/"+fc_vendor]

# Modify default arguments (if none are supplied) to install in ~/usr
if len(sys.argv)==1:
    default_args = 'install --home=~/usr'
    print '*** Adding default arguments to setup:',default_args
    sys.argv += default_args.split()  # it must be a list

# Additional options specific to f2py:
f2py_options = []
if debug_capi:
    f2py_options.append('--debug-capi')

# Define the extension module(s)
extension = Extension(name = name,
                      sources = sources,
                      libraries = libraries,
                      library_dirs = map(expand_sh,library_dirs),
                      f2py_options = f2py_options,
                      )

# Call the actual building/installation routine, in usual distutils form.
setup(name = name,
      description  = description,
      author       = author,
      author_email = author_email,
      ext_modules  = [extension],
      )
