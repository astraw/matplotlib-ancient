#!/usr/bin/env python
from matplotlib.matlab import *

def f(t):
    return cos(2*pi*t) * exp(-t)

t1 = arange(0.0, 5.0, 0.1)
t2 = arange(0.0, 5.0, 0.02)


subplot(211)
l = plot(t1, f(t1), 'bo', t2, f(t2), 'k')
grid(True)
title('A tale of 2 subplots')
ylabel('Damped oscillation')

subplot(212)
plot(t2, cos(2*pi*t2), 'r>')
grid(True)
xlabel('time (s)')
ylabel('Undamped')
savefig('../figures/subplot_demo.png')
savefig('../figures/subplot_demo.eps')
show()

