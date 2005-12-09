from __future__ import division
from pylab import *

def func3(x,y):
    return (1- x/2 + x**5 + y**3)*exp(-x**2-y**2)

dx, dy = 0.025, 0.025
x = arange(-3.0, 3.0, dx)
y = arange(-3.0, 3.0, dy)
X,Y = meshgrid(x, y)

Z = func3(X, Y)

im = imshow(Z, interpolation='bilinear', origin='lower',
            cmap=cm.gray, extent=(-3,3,-3,3))


cset = contour(Z, arange(-1.2,1.6,0.2),
               origin='lower',
               linewidths=2,
               extent=(-3,3,-3,3)
               )

clabel(cset,
       inline=1,
       fmt='%1.1f',
       fontsize=10)


axis('off')
hot()
colorbar()
title('Some like it hot')
show()
