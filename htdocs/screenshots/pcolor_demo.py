from __future__ import division
from matplotlib.matlab import *

def func3(x,y):
    return (1- x/2 + x**5 + y**3)*exp(-x**2-y**2)

dx, dy = 0.025, 0.025
x = arange(-3.0, 3.0, dx)
y = arange(-3.0, 3.0, dy)
X,Y = meshgrid(x, y)

Z = func3(X, Y)
#pcolor(X, Y, Z, shading='flat')       # slow
im = imshow(Z, cmap=ColormapJet(256))  # fast
gca().set_image_extent(-3, 3, -3, 3)
axis('off')

savefig('pcolor_demo_small', dpi=60)
savefig('pcolor_demo_large', dpi=120)

show()
