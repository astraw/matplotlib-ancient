from pylab import *

def func3(x,y):
    return (1- x/2.0 + x**5 + y**3)*exp(-x**2-y**2)

# make these smaller to increase the resolution
dx, dy = 0.05, 0.05
x = arange(-3.0, 3.0, dx)
y = arange(-3.0, 3.0, dy)
X,Y = meshgrid(x, y)
extent = min(x), max(x), min(y), max(y)


# make an 8 by 8 chessboard
Z1 = array(([0,1]*4 + [1,0]*4)*4); Z1.shape = 8,8  
im1 = imshow(Z1, cmap=cm.gray,
             interpolation='nearest', extent=extent)

# prevents the axes from clearing on next command
hold(True)  

Z2 = func3(X, Y)
im2 = imshow(Z2, cmap=cm.jet, alpha=.9,
             interpolation='bilinear',  extent=extent)
axis('off')

savefig('../figures/layer_images.eps')
savefig('../figures/layer_images.png')
show()
