from pylab import *
rc('axes', hold=True)
rc('image', origin='upper')

Z = arange(40000.0); Z.shape = 200,200
Z[:,50:] = 1
im1 = figimage(Z, xo=0,  yo=0)  
im2 = figimage(Z, xo=100, yo=100, alpha=.8)

savefig('../figures/figure_mosaic.eps')
savefig('../figures/figure_mosaic.png', dpi=72)

show()

    
