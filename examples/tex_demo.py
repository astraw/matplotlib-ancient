#!/usr/bin/env python

from pylab import *

rc('text', usetex= True)

figure(1)
ax = axes([0.1, 0.1, 0.8, 0.7])
t = arange(0.0, 1.0+0.01, 0.01)
s = cos(2*2*pi*t)
plot(t, s)

xlabel('time (s)')
ylabel('voltage (mV)')
title(r"\TeX\ is Number $e^{-i\pi}$!", fontsize=30)
grid(True)

show()
