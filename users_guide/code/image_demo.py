from pylab import *

delta = 0.025
# generate a mesh of x and y vectors
x = y = arange(-3.0, 3.0, delta)
X, Y = meshgrid(x, y)
# create 2D gaussian distributions
Z1 = bivariate_normal(X, Y, 1.0, 1.0, 0.0, 0.0)
Z2 = bivariate_normal(X, Y, 1.5, 0.5, 1, 1)

# plot the difference of Gaussians with blinear interpolation
im = imshow(Z2-Z1, interpolation='bilinear')
axis('off')
savefig('../figures/image_demo.eps')
savefig('../figures/image_demo.png')
show()

