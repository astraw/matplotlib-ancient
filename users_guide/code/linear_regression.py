from pylab import *

# Generate some test data; y is a linear function of x + nse
x = arange(0.0, 2.0, 0.05)
nse = 0.3*randn(len(x)) 
y = 2+ 3*x + nse

# the bestfit line from polyfit; you can do arbitrary order
# polynomials but here we take advantage of a line being a first order
# polynomial
m,b = polyfit(x,y,1)  

# plot the data with blue circles and the best fit with a thick
# solid black line
plot(x, y, 'bo', x, m*x+b, '-k', linewidth=2)
ylabel('regression')
grid(True)       

# save the image to hardcopy
savefig('../figures/linear_regression.eps')
savefig('../figures/linear_regression.png')

show()
