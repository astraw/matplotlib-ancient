from pylab import *
t = arange(0.0, 5.2, 0.2)
plot(t, t, 'b--', t, t**2, 'bs', t, t**3, 'g^')
savefig('thirdfig')
show()
