from matplotlib.matlab import *

t = arange(0.1, 4, 0.1)
s = exp(-t)
e = 0.1*randn(len(s))
f = 0.1*randn(len(s))
g = 0.1*randn(len(s))
h = 0.1*randn(len(s))

xyerrorbar(t, s, e, f, g, h, fmt='o')
xlabel('Distance (m)')
ylabel('Height (m)')
title('Mean and standard error as a function of distance')
show()
