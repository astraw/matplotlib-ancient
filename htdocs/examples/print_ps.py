from matplotlib.matlab import *

t = arange(0.0, 2.0, 0.01)
s1 = sin(2*pi*t)
s2 = sin(2*2*pi*t)
plot(t, s1, 'r-', t, s2, 'g--')
legend( ('Signal1', 'Signal2') )
xlabel('time')
ylabel('volts')
#savefig('test.ps')
title('This is a recording')
show()
