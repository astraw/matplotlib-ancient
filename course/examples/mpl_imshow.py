from pylab import *
x = arange(100.0); x.shape = 10,10
im = imshow(x, interpolation='nearest')
colorbar()
savefig('../fig/mpl_image_jet')

im.set_interpolation('bilinear')
hot()
savefig('../fig/mpl_image_hot')
