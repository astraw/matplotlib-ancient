from pylab import *

def f(t):
    'a damped oscillation'
    return cos(2*pi*t) * exp(-t)

t1 = arange(0.0, 5.0, 0.1)
t2 = arange(0.0, 5.0, 0.02)

# the upper subplot; 2 rows, 1 column, subplot #1
subplot(211)
l = plot(t1, f(t1), 'bo', t2, f(t2), 'k')
grid(True)
title('A tale of 2 subplots')
ylabel('Damped oscillation')

# the lower subplot; 2 rows, 1 column, subplot #2
subplot(212)
plot(t2, cos(2*pi*t2), 'r>')
grid(True)
xlabel('time (s)')
ylabel('Undamped')

savefig('../figures/subplot_demo.png')
savefig('../figures/subplot_demo.eps')
show()

