import os, sys

from hthelpers import modules
os.system('rm -rf docs matplotlib; mkdir docs')
os.system('cd docs; /usr/local/bin/pydoc -w %s' % ' '.join(modules))

devTree, thisDir = os.path.split( os.getcwd() )
for modname in modules:
    print '\tConverting %s to template' % modname
    s = file('docs/' + modname + '.html').read()
    s = s.replace('file:%s' % devTree, '')
    s = s.replace(devTree, '')
    lines = s.split('\n')
    outLines = ['@header@']
    outLines.extend(lines[5:-1])
    outLines.append('@footer@')
    outFile = file(modname + '.html.template', 'w')
    outFile.write('\n'.join(outLines))    
