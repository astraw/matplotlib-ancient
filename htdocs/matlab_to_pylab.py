# As was recently discussed on the matplotlib users mailing list, we
# were concerned that the module name matplotlib.matlab might infringe
# on The Mathwork's trademark of matlab, and so the matlab module has
# been renamed pylab -
# http://sourceforge.net/mailarchive/message.php?msg_id=10174321
#
# matplotlib/matlab.py was renamed to matplotlib/pylab.py and any
# script which used matplotlib.matlab can now use matplotlib.pylab
# transparently in it's place.  Howver, a new file called pylab.py,
# which simply imports matplotlib.pylab, is now placed in
# site-packages,
#
# from matplotlib.matlab import *     # old, deprecated
# from matplotlib.pylab import *      # new replacement
# from pylab import *                 # new shortcut
# 
# This script will recursively convert all files and directories
# listed in sys.argv from usages of matplotlib.matlab to the new pylab
# convention.
#
# This script replaces the following strings
#
#   matplotlib.matlab                   -> pylab
#   from matplotlib import matlab as    -> from matplotlib import pylab as 
#   _matlab_helpers                     -> _pylab_helpers
#   matlab interface                    -> pylab interface
#
# Note it does not fix scripts which use
#
#   from matplotlib import matlab
#   matlab.something()
#
# unless you give the flag --force which will then also replace *all*
# uses of "matlab" with "pylab"
#
# Only files in the list of extensions listed below will be opertated
# on.  You can customize this list.
#
# Example usage
# > cd myscriptdir
# > python ~/somedir/matlab_to_pylab.py *

extensions =('.py', '.template', '.html')

from matplotlib.cbook import get_recursive_filelist
import os, sys

# replace all usages of matlab -> pylab if force
if '--force' in sys.argv:
    replace = (('matlab', 'pylab'),)
    sys.argv.remove('--force')
else:
    replace = (
        ('matplotlib.matlab', 'pylab'),        
        ('from matplotlib import matlab as', 'from matplotlib import pylab as'),
        ('_matlab_helpers', '_pylab_helpers'),
        ('matlab interface', 'pylab interface'),        
        )


def usefile(fname):
    basename, ext = os.path.splitext(fname)
    if ext in extensions: return True
    return False
fnames = [fname for fname in get_recursive_filelist(sys.argv[1:]) if usefile(fname)]

def clean_fname(fname):
    s = file(fname, 'r').read()
    for old, new in replace:
        s = s.replace(old, new)
    file(fname, 'w').write(s)
    
for fname in fnames:
    if fname==sys.argv[0]: continue  # do not clean self
    print 'cleaning', fname
    clean_fname(fname)

