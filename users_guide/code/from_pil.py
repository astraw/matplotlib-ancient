import Image
from pylab import *

im = Image.open('../data/leo_ratner.jpg')
s = im.tostring()    # convert PIL image -> string

# convert string -> numerix array of floats
rgb = fromstring(s, UInt8).astype(Float)/255.0  

# resize to RGB array
rgb = resize(rgb, (im.size[1], im.size[0], 3))

imshow(rgb, interpolation='nearest')
axis('off')  # don't display the image axis
show()
