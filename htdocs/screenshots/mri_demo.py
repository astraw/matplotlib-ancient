from pylab import *

# data are 256x256 16 bit integers
dfile = '../../examples/data/s1045.ima'
im = fromstring(file(dfile).read(), UInt16).astype(Float)
im.shape = 256, 256

imshow(im)
axis('off')
savefig('mri_demo_small', dpi=50)
savefig('mri_demo_large', dpi=100)
show()
