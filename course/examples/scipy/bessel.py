"""Plot some Bessel functions of integer order, using Scipy and pylab"""

import scipy as S
import pylab as P

# shorthand
special = S.special

def jn_asym(n,x):
    """Asymptotic form of jn(x) for x>>n"""
    
    return S.sqrt(2.0/S.pi/x)*S.cos(x-(n*S.pi/2.0+S.pi/4.0))

# build a range of values to plot in
x = P.frange(0,30,npts=400)

# Start by plotting the well-known j0 and j1
P.figure()
P.plot(x,special.j0(x),label='j0')
P.plot(x,special.j1(x),label='j1')

# Show a higher-order Bessel function
n = 5
P.plot(x,special.jn(n,x),label='j%s' % n)

# and compute its asymptotic form (valid for x>>n, where n is the order).  We
# must first find the valid range of x where at least x>n:
x_asym = S.compress(x>n,x)
P.plot(x_asym,jn_asym(n,x_asym),label='j%s (asymptotic)' % n)

# Finish off the plot
P.legend()
P.title('Bessel Functions')
# horizontal line at 0 to show x-axis, but after the legend
P.axhline(0)

# EXERCISE: redo the above, for the asymptotic range 0<x<<n.  The asymptotic
# form in this regime is
# J(n,x) = (1/gamma(n+1))(x/2)^n

# Now, let's verify numerically the recursion relation
# J(n+1,x) = (2n/x)J(n,x)-J(n-1,x)
jn = special.jn  # just a shorthand

# Be careful to check only for x!=0, to avoid divisions by zero
xp = S.compress(x>0.0,x)  # positive x

# construct both sides of the recursion relation, these should be equal
j_np1 = jn(n+1,xp)
j_np1_rec = (2.0*n/xp)*jn(n,xp)-jn(n-1,xp)

# Now make a nice error plot of the difference, in a new figure
P.figure()
P.semilogy(xp,abs(j_np1-j_np1_rec),'r+-')
P.title('Error in recursion for J%s' % n)
P.grid()

# Don't forget a show() call at the end of the script
P.show()
