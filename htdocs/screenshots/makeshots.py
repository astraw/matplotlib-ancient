"""
setenv TTFPATH ~/src/ttf_microsoft/

"""
import sys, os

default = 'Agg'
# do not remove the pngs - some are screenshots!
files = {
    'layer_images.py'   : default,        
    'finance_work2.py'  : default,    
    'simple_plot.py'    : default, 
    'axes_demo.py'      : default, 
    'histogram_demo.py' : default, 
    'mri_with_eeg.py'   : default,
    'fill_demo.py'      : default,
    'date_demo.py'      : default,         
    'barchart_demo.py'  : default,
    'table_demo.py'     : default, 
    'legend_demo.py'    : default,
    'mathtext_demo.py'  : default,     
    'pcolor_demo.py'    : default, 
    'text_themes.py'    : default, 
    'log_shot.py'       : default,
    'align_text.py'     : default,          
    'scatter_demo2.py'  : default, 

    }

figsize = 'figsize=(8,6)'
dpi1 = 60
dpi2 = 120
def make_shot(fname, backend):
    lines = [
        'from __future__ import division\n',
        'import matplotlib\n',
        'matplotlib.use("%s")\n' % backend,
        'from matplotlib.matlab import *\n'
        'figure(%s)\n' % figsize,
        ]
    
    print '\tdriving %s' % fname
    for line in file(fname):
        if line.strip().startswith('from __future__ import division'): continue
        if line.strip().startswith('matplotlib.use'): continue
        if line.strip().startswith('savefig'): continue
        if line.strip().startswith('from matplotlib.matlab import *'): continue
        if line.strip().startswith('show'): continue
        lines.append(line)
    basename, ext = os.path.splitext(fname)
    lines.append('savefig("%s_small", dpi=%d)\n' % (basename, dpi1))
    lines.append('savefig("%s_large", dpi=%d)\n' % (basename, dpi2))
    tmpfile = '_tmp_%s.py' % basename
    file(tmpfile, 'w').write(''.join(lines))
    os.system('python %s' % tmpfile)
    #os.remove(tmpfile)
    
for fname, backend in files.items():
    make_shot(fname, backend)



