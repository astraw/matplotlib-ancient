import os, sys, glob, shutil
import matplotlib
MPL_SRC = '/home/jdhunter/python/projects/matplotlib'

#copy all the examples to the htdocs examples dir
for pathname in glob.glob(os.path.join(MPL_SRC, 'examples', '*.py')):
    path, fname = os.path.split(pathname)
    newname = os.path.join('examples', fname)
    print 'copying %s to %s' % (pathname, newname)
    shutil.copy(pathname, fname)

filenames = ( '.matplotlibrc', 'INSTALL', 'CHANGELOG',
              'NUMARRAY_ISSUES', 'API_CHANGES',)
for fname in filenames:
    oldname = os.path.join(MPL_SRC,fname)
    print 'copying %s to %s' % (oldname, fname)
    shutil.copy(oldname, fname)
                           

# auto-generate the license file with the right version number
fmt = file('license.fmt').read()
d = {'version':matplotlib.__version__}
print >> file('license.html.template','w'), fmt%d


print 'Making screenshots'
os.system('cd screenshots; python makeshots.py')

print 'Running process_docs'
os.system('python process_docs.py')

print 'Running convert'
os.system('python convert.py')

print 'Building archive'
os.system('tar cfz site.tar.gz *.html screenshots tut examples gd .matplotlibrc CHANGELOG NUMARRAY_ISSUES  API_CHANGES')
