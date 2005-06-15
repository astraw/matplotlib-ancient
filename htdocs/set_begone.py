"""
Please backup entire directory recursively before running this script
"""
from matplotlib.cbook import listFiles

for fname in listFiles('.', '*.py'):

    lines = []
    cnt = 0
    for line in file(fname):
        if line.lstrip().startswith('set('):
            line = line.replace('set(', 'setp(')
            cnt +=1
        if line.lstrip().startswith('get('):
            line = line.replace('get(', 'getp(')
            cnt +=1
        lines.append(line)
        
    file(fname, 'w').writelines(lines)
    print '%s\t: %d replacements'%(fname,cnt)
