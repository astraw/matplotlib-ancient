#!/usr/bin/env python
from __future__ import division
from matplotlib.matlab import *

def func3(x,y):
    return (1- x/2 + x**5 + y**3)*exp(-x**2-y**2)


# make these smaller to increase the resolution
dx, dy = 0.05, 0.05

x = arange(-3.0, 3.0, dx)
y = arange(-3.0, 3.0, dy)
X,Y = meshgrid(x, y)
Z = func3(X, Y)
ax1 = axes([0.1, 0.1, 0.6, 0.8])

cmap = ColormapJet()
cmin, cmax = 0, 1
cmap.set_clim(cmin, cmax)

ax1.pcolor(X, Y, Z, shading='flat', cmap=cmap)

ax2 = axes([0.75, 0.1, 0.1, 0.8])
N = 100
c = linspace(cmin,cmax,100)
C = array([c,c])
ax2.pcolor(transpose(C), shading='flat', cmap=cmap)
ax2.set_xticks([])
ax2.yaxis.tick_right()
ticks = arange(0,N+1,20)
ax2.set_yticks(ticks)
ax2.set_yticklabels(['%1.1f'%(float(tick)/N) for tick in ticks])




show()

    
