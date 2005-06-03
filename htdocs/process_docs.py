import os, sys

from hthelpers import modules
os.system('rm -rf docs matplotlib; mkdir docs')
for m in modules:
    os.system('cd docs; pydoc -w %s' % m)

devTree, thisDir = os.path.split( os.getcwd() )
for modname in modules:
    print '\tConverting %s to template' % modname
    try: s = file('docs/' + modname + '.html').read()
    except IOError: continue
    s = s.replace('file:%s' % devTree, '')
    s = s.replace(devTree, '')
    lines = s.split('\n')
    outLines = ['@header@']
    outLines.extend(lines[5:-1])
    outLines.append('@footer@')
    outFile = file(modname + '.html.template', 'w')
    outFile.write('\n'.join(outLines))    
