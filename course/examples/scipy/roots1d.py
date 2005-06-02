import scipy as S
import pylab as P

coefs = [  1. ,  -3.5,  -0.5,  11. , -17. ,   6. ]

pol = S.poly1d(coefs)

x = P.frange(-4,4,npts=400)
y = pol(x)

P.figure()
P.plot(x,y)
P.axhline(0)
P.ylim(-100,100)

print 'Coefficients of p(x):',coefs
print 'Roots of p(x):',pol.r

P.show()


