from pylab import *

def f(t):
    s1 = cos(2*pi*t)
    e1 = exp(-t)
    return multiply(s1,e1)

t1 = arange(0.0, 5.0, 0.1)
t2 = arange(0.0, 5.0, 0.02)

figure(1)
subplot(211)
plot(t1, f(t1), 'bo', t2, f(t2), 'k')

subplot(212)
plot(t2, cos(2*pi*t2), 'r--')
savefig('subplot')
show()
