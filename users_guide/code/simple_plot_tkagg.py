from matplotlib.matlab import *
plot([1,2,3])

xlabel('time (s)')
ylabel('volts')
title('A really simple plot')
grid(True)

t = arange(0.0, 3.0, 0.05)  # in matlab t = [0.0: 0.05: 3.0];
s = sin(2*pi*t)
plot(t,s)

hold(False)
plot(t, s)

clf()   # clear the figure
t = arange(0.0, 5.0, 0.05)
s1 = sin(2*pi*t)
s2 = s1 * exp(-t)
plot(t, s1, t, s2)

clf()   
plot(t, s1, 'g--o', t, s2, 'r:s')
legend(('sine wave', 'damped exponential'))
savefig('../figures/plot_styles.png')
savefig('../figures/plot_styles.eps')


plot(t, s1, markersize=15, marker='d', \
     markerfacecolor='g', markeredgecolor='r')

clf()
lines = plot(t, s1)
set(lines, markersize=15, marker='d', \
    markerfacecolor='g', markeredgecolor='r')

clf()
line, = plot(t, s1)
line.set_markersize(15)
line.set_marker('d')
line.set_markerfacecolor('g')
line.set_markeredgecolor('r')
draw()
savefig('../figures/big_diamonds.png')
savefig('../figures/big_diamonds.eps')
