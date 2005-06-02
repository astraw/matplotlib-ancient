"""Simple data fitting and smoothing example"""

from scipy import exp, arange,array
from RandomArray import normal
from scipy.optimize import leastsq
from scipy.interpolate import splrep,splev

import pylab as P

parsTrue = array([2.0, -.76, 0.1])
distance = arange(0, 4, 0.001)

def func(pars):
    a, alpha, k = pars
    return a*exp(alpha*distance) + k

def errfunc(pars):
    return data - func(pars)  #return the error

# some pseudo data; add some noise
data = func(parsTrue) + normal(0.0, 0.1, distance.shape)

# the intial guess of the params
guess = 1.0, -.4, 0.0

# now solve for the best fit paramters
best, info, ier, mesg = leastsq(errfunc, guess, full_output=1)

print 'true', parsTrue
print 'best', best

print 'Spline smoothing of the data'
sp = splrep(distance,data)
smooth = splev(distance,sp)
print 'Spline information (see splrep and splev for details):',sp

# Now use pylab to plot
P.figure()
P.plot(distance,data,label='Noisy data')
P.plot(distance,func(best),lw=2,label='Best fit')
P.legend()
P.figure()
P.plot(distance,data,label='Noisy data')
P.plot(distance,smooth,lw=2,label='Spline-smoothing')
P.legend()
P.show()
