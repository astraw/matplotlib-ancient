from pylab import *

x = arange(100.0); x.shape = 10,10

subplot(211)
title('blue should be up')
imshow(x, origin='upper', interpolation='nearest')

subplot(212)
title('blue should be down')
imshow(x, origin='lower', interpolation='nearest')

savefig('../figures/image_origin.eps')
savefig('../figures/image_origin.png')
show()
