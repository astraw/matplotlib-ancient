import os

files = ( 'first_fig.py', 'second_fig.py', 'subplot.py',
          'text_dict.py', 'thirdfig.py', 'silly_axes.py',
          'test.py', 'text_simple.py', 'mathtext_tut.py', 'date_demo2.py')

for fname in files:
    print 'Running', fname
    os.system('python %s' % fname)
    

