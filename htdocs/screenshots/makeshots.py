import sys, os

files = ('simple_plot.py', 'axes_demo.py', 'histogram_demo.py',
         'mri_with_eeg.py', 'barchart_demo.py', 'legend_demo.py',
         'pcolor_demo.py', 'text_themes.py', 'log_shot.py',
         'scatter_demo2.py')

for file in files:
    print 'Making screenshot', file
    os.system('python %s' % file)




