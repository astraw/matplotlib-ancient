#!/usr/bin/env python
"""
pcolormesh uses a QuadMesh, a faster generalization of pcolor, but
with some restrictions.
"""

from matplotlib.mlab import linspace, meshgrid
import matplotlib.numerix as nx
from pylab import figure,show
import matplotlib.numerix.ma as ma
from matplotlib import cm, colors

n = 56
x = linspace(-1.5,1.5,n)
X,Y = meshgrid(x,x);
Qx = nx.cos(Y) - nx.cos(X)
Qz = nx.sin(Y) + nx.sin(X)
Qx = (Qx + 1.1)
Z = nx.sqrt(X**2 + Y**2)/5;
Z = (Z - nx.mlab.amin(Z)) / (nx.mlab.amax(Z) - nx.mlab.amin(Z))

# The color array can include masked values:
Zm = ma.masked_where(nx.fabs(Qz) < 0.5*nx.mlab.amax(Qz), Z)


fig = figure()
ax = fig.add_subplot(121)
ax.pcolormesh(Qx,Qz,Z)
ax.set_title('Without masked values')

ax = fig.add_subplot(122)
cmap = cm.jet
cmap.set_bad('w', 1.0)
# We need to specify the norm so we can set clip to False;
# probably this should be fixed so it would not be necessary.
norm = colors.normalize(clip = False)
ax.pcolormesh(Qx,Qz,Zm, cmap=cmap, norm=norm)
ax.set_title('With masked values')
show()

