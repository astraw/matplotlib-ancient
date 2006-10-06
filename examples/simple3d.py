#!/usr/bin/env python

import matplotlib
matplotlib.rcParams['numerix'] = 'numpy'
import numpy as np
from numpy import arange, cos, linspace, ones, pi, sin
import matplotlib.numerix as nx
from matplotlib.numerix import outerproduct

import pylab
import matplotlib.axes3d as axes3d


fig = pylab.gcf()

ax3d = axes3d.Axes3D(fig)
plt = fig.axes.append(ax3d)

delta = pi / 199.0
u = arange(0, 2*pi+(delta*2), delta*2)
v = arange(0, pi+delta, delta)

x = outerproduct(cos(u),sin(v))
y = outerproduct(sin(u),sin(v))
z = outerproduct(ones(u.shape), cos(v))

#ax3d.plot_wireframe(x,y,z)
surf = ax3d.plot_surface(x, y, z)
surf.set_array(linspace(0, 1.0, len(v)))
        
ax3d.set_xlabel('X')
ax3d.set_ylabel('Y')
ax3d.set_zlabel('Z')

pylab.show()
#pylab.savefig('simple3d.svg')
