from gui_thread import wxPython_thread
wxPython_thread.wxPython_thread()
print 'made it 1'

import matplotlib
matplotlib.use('WX')
from matplotlib.matlab import *
from matplotlib.backends.backend_wx import flush_draw, ShowOn
ShowOn().set(True)

print 'made it 2'
t = arange(0.0, 3.0, 0.01)
for i in range(1,10):
    print 'figure %d' % i    
    figure(1)
    print 'figure' % i
    s = sin(2*pi*i*t)
    plot(t,s)
    #savefig('plot%02d' % i)
    print 'here'
    flush_draw()
    #close(1)
