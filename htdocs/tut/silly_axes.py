from pylab import *

t = arange(0, 2.1, 0.1)

rc('grid', color=0.75, linewidth=1.5)
rc('tick', color='b', labelsize=14)
a = subplot(111)
plot(t, t**2, '-')
title('Custom axes using rc')
grid(True)
savefig('custom_axes')

show()
