#!/usr/bin/env python
"""
An example of how to interact with the plotting canvas by connecting
to move and click events
"""
from matplotlib.matlab import *

t = arange(0.1, 9.0, 0.01)
s = sin(2*pi*t)
ax = subplot(111)
ax.semilogx(t,s)



show()
