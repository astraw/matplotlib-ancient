import os, sys, glob, shutil
import matplotlib
MPL_SRC = '/home/jdhunter/python/projects/matplotlib'

#copy all the examples to the htdocs examples dir
for fname in glob.glob('examples/*.py*'):
    os.remove(fname)
    
for pathname in glob.glob(os.path.join(MPL_SRC, 'examples', '*.py')):
    path, fname = os.path.split(pathname)
    if fname.startswith('_tmp'): continue
    newname = os.path.join('examples', fname)
    print 'copying %s to %s' % (pathname, newname)
    shutil.copy(pathname, newname)

widgetfiles = glob.glob(os.path.join(MPL_SRC, 'examples', 'widgets', '*.py'))
widgetfiles.append(os.path.join(MPL_SRC, 'examples', 'widgets', 'README'))
for pathname in widgetfiles:
    path, fname = os.path.split(pathname)
    if fname.startswith('_tmp'): continue
    newname = os.path.join('examples', 'widgets', fname)
    print 'copying %s to %s' % (pathname, newname)
    shutil.copy(pathname, newname)
    
os.system('zip -r -o matplotlib_examples_%s.zip examples'%matplotlib.__version__)

os.system('cp ../users_guide/users_guide.pdf users_guide_%s.pdf'%matplotlib.__version__)

filenames = ( 'matplotlibrc', 'INSTALL', 'CHANGELOG',
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
#os.system('cd screenshots; python makeshots.py; rm -f _tmp*.py')

print 'Making tutorial images'
#os.system('cd tut; python runall.py')

print 'Running process_docs'
os.system('python process_docs.py')

print 'Running convert'
os.system('python convert.py')

print 'Building archive'
version = matplotlib.__version__
os.system('tar cfz site.tar.gz *.html users_guide_%(version)s.pdf matplotlib_examples_%(version)s.zip screenshots tut examples gd matplotlibrc CHANGELOG NUMARRAY_ISSUES  API_CHANGES set_begone.py'%locals())
