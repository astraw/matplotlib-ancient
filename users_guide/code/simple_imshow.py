# create a random MxN numerix array and plot it as an axes image
from matplotlib.matlab import *
X = rand(20,20)
im = imshow(X)
show()
