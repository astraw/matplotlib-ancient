from pylab import *

# Generate some test data; y is a poly function of x + nse
x = arange(0.0, 2.0, 0.05)
nse = 0.6*randn(len(x)) 
y = 1.1 + 3.2*x + 0.1*x**2 + 2*x**3 + nse

# the bestfit line from polyfit
coeffs = polyfit(x,y,3)  

# plot the data with blue circles and the best fit with a thick
# solid black line
besty = polyval(coeffs, x)
plot(x, y, 'bo', x, besty, '-k', linewidth=2)
ylabel('polynomial regression')
grid(True)       

# save the image to hardcopy
savefig('../figures/poly_regression.eps')
savefig('../figures/poly_regression.png')

show()
