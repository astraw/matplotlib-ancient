#!/usr/bin/env python
"""
You can use TeX to render all of your matplotlib text if the rc
parameter text.usetex is set.  This works currently on the agg and ps
backends, and requires that you have tex and the other dependencies
described at http://matplotlib.sf.net/matplotlib.texmanager.html
properly installed on your system.  The first time you run a script
you will see a lot of output from tex and associated tools.  The next
time, the run may be silent, as a lot of the information is cached in
~/.tex.cache

"""
from matplotlib import rc
from matplotlib.numerix import arange, cos, pi
from pylab import figure, axes, plot, xlabel, ylabel, title, \
     grid, savefig, show


rc('text', usetex=True)
figure(1)
ax = axes([0.1, 0.1, 0.8, 0.7])
t = arange(0.0, 1.0+0.01, 0.01)
s = cos(2*2*pi*t)+2
plot(t, s)

xlabel(r'\bf{time (s)}')
ylabel(r'\it{voltage (mV)}',fontsize=16)
title(r"\TeX\ is Number $\displaystyle\sum_{n=1}^\infty\frac{-e^{i\pi}}{2^n}$!", 
      fontsize=16, color='r')
grid(True)
savefig('tex_demo.eps')
savefig('jdh.ps')

show()
