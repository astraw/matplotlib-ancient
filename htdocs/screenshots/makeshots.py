import sys, os

default = 'Agg'
# do not remove the pngs - some are screenshots!
files = {'simple_plot.py'    : default, 
         'axes_demo.py'      : default,   # a color bug
         'histogram_demo.py' : default, 
         #'mri_with_eeg.py'   : default, 
         'barchart_demo.py'  : default,
         'table_demo.py'     : default, 
         'legend_demo.py'    : default, 
         #'pcolor_demo.py'    : default, 
         'text_themes.py'    : 'GTK',   # font problem
         'log_shot.py'       : default,
         'align_text.py'     : default,          
         'scatter_demo2.py'  : 'Agg',    # color bug, some circles not filled
         }

for fname, backend in files.items():
    print 'Making screenshot', fname
    os.system('python %s -d%s' % (fname, backend))




