from __future__ import division
from pylab import *

def func3(x,y):
    return (1- x/2 + x**5 + y**3)*exp(-x**2-y**2)

dx, dy = 0.025, 0.025
x = arange(-3.0, 3.0, dx)
y = arange(-3.0, 3.0, dy)
X,Y = meshgrid(x, y)

Z = func3(X, Y)
#pcolor(X, Y, Z, shading='flat')       # slow
title('Some like it hot')
im = imshow(Z, cmap=cm.hot, extent=(-3, 3, -3, 3))  # fast
axis('off')
colorbar()

savefig('pcolor_demo_small', dpi=60)
savefig('pcolor_demo_large', dpi=120)

show()
