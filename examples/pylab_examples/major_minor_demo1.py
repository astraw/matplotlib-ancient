#!/usr/bin/env python
"""
Demonstrate how to use major and minor tickers.

The two relevant userland classes are Locators and Formatters.
Locators determine where the ticks are and formatters control the
formatting of ticks.

Minor ticks are off by default (NullLocator and NullFormatter).  You
can turn minor ticks on w/o labels by setting the minor locator.  You
can also turn labeling on for the minor ticker by setting the minor
formatter

Make a plot with major ticks that are multiples of 20 and minor ticks
that are multiples of 5.  Label major ticks with %d formatting but
don't label minor ticks

The MultipleLocator ticker class is used to place ticks on multiples of
some base.  The FormatStrFormatter uses a string format string (eg
'%d' or '%1.2f' or '%1.1f cm' ) to format the tick

The pylab interface grid command chnages the grid settings of the
major ticks of the y and y axis together.  If you want to control the
grid of the minor ticks for a given axis, use for example

  ax.xaxis.grid(True, which='minor')

Note, you should not use the same locator between different Axis
because the locator stores references to the Axis data and view limits

"""

from pylab import *
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

majorLocator   = MultipleLocator(20)
majorFormatter = FormatStrFormatter('%d')
minorLocator   = MultipleLocator(5)


t = arange(0.0, 100.0, 0.1)
s = sin(0.1*pi*t)*exp(-t*0.01)

ax = subplot(111)
plot(t,s)

ax.xaxis.set_major_locator(majorLocator)
ax.xaxis.set_major_formatter(majorFormatter)

#for the minor ticks, use no labels; default NullFormatter
ax.xaxis.set_minor_locator(minorLocator)

show()
