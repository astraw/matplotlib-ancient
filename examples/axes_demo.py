#!/usr/bin/env python
 
from pylab import *

# create some data to use for the plot
dt = 0.001
t = arange(0.0, 10.0, dt)
r = exp(-t[:1000]/0.05)               # impulse response
x = randn(len(t))
s = convolve(x,r,mode=2)[:len(x)]*dt  # colored noise

# the main axes is subplot(111) by default
plot(t, s)
axis([0, 1, 1.1*amin(s), 2*amax(s) ])
xlabel('time (s)')
ylabel('current (nA)')
title('Gaussian colored noise')

# this is an inset axes over the main axes
a = axes([.65, .6, .2, .2], axisbg='y')
n, bins, patches = hist(s, 400, normed=1)
title('Probability')
set(a, xticks=[], yticks=[])

# this is another inset axes over the main axes
a = axes([0.2, 0.6, .2, .2], axisbg='y')
plot(t[:len(r)], r)
title('Impulse response')
set(a, xlim=(0,.2), xticks=[], yticks=[])
    
#savefig('../figures/axes_demo.eps')
#savefig('../figures/axes_demo.png')
show()
