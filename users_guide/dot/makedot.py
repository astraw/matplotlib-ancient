import os, sys
from glob import glob

for fname in glob("*.dot"):
    basename, ext = os.path.splitext(fname)
    print 'dotting', fname
    os.system('dot -Tps -o ../figures/%s.ps %s'%(basename, fname))
    os.system('convert -density 600x600 ../figures/%s.ps ../figures/%s.png'%(basename, basename))
