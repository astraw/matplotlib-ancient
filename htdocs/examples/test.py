from matplotlib.matlab import *
X = rand(5,10)
im = imshow(X)
im.set_interpolation('nearest')
show()
