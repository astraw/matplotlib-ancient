import os, sys

files = ( 'matplotlib.cbook.html', 'matplotlib.afm.html',
          'matplotlib.lines.html', 'matplotlib.patches.html',
          'matplotlib.artist.html', 'matplotlib.axes.html',
          'matplotlib.backend_bases.html', 'matplotlib.matlab.html',
          'matplotlib.mlab.html',
          'matplotlib.transforms.html',
          'matplotlib.backends.backend_gd.html',
          'matplotlib.backends.backend_gtk.html',
          'matplotlib.backends.backend_ps.html',
          'matplotlib.backends.backend_template.html',
          'matplotlib.backends.backend_wx.html',
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
    
