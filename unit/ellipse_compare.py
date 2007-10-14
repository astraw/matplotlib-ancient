"""
Compare the ellipse generated with arcs versus a polygonal approximation 
"""
import numpy as npy
from matplotlib import patches
from pylab import figure, show

xcenter, ycenter = 0.38, 0.52
#xcenter, ycenter = 0., 0.
width, height = 1e-1, 3e-1
angle = -30

theta = npy.arange(0.0, 360.0, 1.0)*npy.pi/180.0
x = width/2. * npy.cos(theta)
y = height/2. * npy.sin(theta)

rtheta = angle*npy.pi/180.
R = npy.array([
    [npy.cos(rtheta),  -npy.sin(rtheta)],
    [npy.sin(rtheta), npy.cos(rtheta)],
    ])


x, y = npy.dot(R, npy.array([x, y]))
x += xcenter
y += ycenter

fig = figure()
ax = fig.add_subplot(211, aspect='auto')
ax.fill(x, y, alpha=0.2, facecolor='yellow')

e1 = patches.Ellipse((xcenter, ycenter), width, height,
             angle=angle, linewidth=2, fill=False)

ax.add_artist(e1)

ax = fig.add_subplot(212, aspect='equal')
ax.fill(x, y, alpha=0.2, facecolor='yellow')
e2 = patches.Ellipse((xcenter, ycenter), width, height,
             angle=angle, linewidth=2, fill=False)


ax.add_artist(e2)
ax.autoscale_view()


ax.set_xlim(0.2, .5)
ax.set_ylim(0.3, 0.7)

#fig.savefig('ellipse_compare.png')
#fig.savefig('ellipse_compare.ps')

show()
