import os, sys

files = (
    'matplotlib.afm.html',
    'matplotlib.artist.html',
    'matplotlib.axes.html',
    'matplotlib.axis.html',    
    'matplotlib.backend_bases.html',
    'matplotlib.backends.backend_gd.html',
    'matplotlib.backends.backend_gtk.html',
    'matplotlib.backends.backend_gtkgd.html',    
    'matplotlib.backends.backend_ps.html',
    'matplotlib.backends.backend_template.html',
    'matplotlib.backends.backend_wx.html',
    'matplotlib.cbook.html',
    'matplotlib.figure.html',            
    'matplotlib.legend.html',        
    'matplotlib.lines.html',
    'matplotlib.matlab.html',
    'matplotlib.mlab.html',
    'matplotlib.patches.html',
    'matplotlib.text.html',
    'matplotlib.transforms.html',
          )


devTree, thisDir = os.path.split( os.getcwd() )
for fname in files:
    print '\tConverting %s to template' % fname
    s = file('../docs/' + fname).read()
    s = s.replace('file:%s' % devTree, '')
    s = s.replace(devTree, '')
    lines = s.split('\n')
    outLines = ['@header@']
    outLines.extend(lines[5:-1])
    outLines.append('@footer@')
    outFile = file(fname + '.template', 'w')
    outFile.write('\n'.join(outLines))
    
