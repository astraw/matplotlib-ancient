import sys, os

# do not remove the pngs - some are screenshots!
files = {'simple_plot.py'    : 'GD', 
         'axes_demo.py'      : 'GTK',   # a color bug
         'histogram_demo.py' : 'GD', 
#         'mri_with_eeg.py'   : 'GD',   # bug in eeg offset
         'barchart_demo.py'  : 'GD', 
         'legend_demo.py'    : 'GD', 
         'pcolor_demo.py'    : 'GD', 
         'text_themes.py'    : 'GTK',   # font problem
         'log_shot.py'       : 'GD', 
         'scatter_demo2.py'  : 'GD',    # color bug, some circles not filled
         }

for fname, backend in files.items():
    print 'Making screenshot', fname
    os.system('python %s -d%s' % (fname, backend))




