#!/usr/bin/env python
"""

Demonstrate how to do two plots on the same axes with different left
right scales.


The trick is to use *2 different axes*.  Turn the axes rectangular
frame off on the 2nd axes to keep it from obscuring the first.
Manually set the tick locs and labels as desired.  You can use
separate matplotlib.ticker formatters and locators as desired since
the two axes are independent

To do the same with different x scales, use the xaxis instance and
call tick_bottom and tick_top in place of tick_left and tick_right

"""

from pylab import *

ax1 = subplot(111)
t = arange(0.01, 10.0, 0.01)
s1 = exp(t)
plot(t, s1, 'b-')
xlabel('time (s)')
ylabel('exp')


# turn off the 2nd axes rectangle with frameon kwarg
ax2 = twinx()
s2 = sin(2*pi*t)
plot(t, s2, 'r.')
ylabel('sin')
#xlim(0.01, 10)
#set(gca(), xscale='log')

show()
