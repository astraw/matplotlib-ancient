from matplotlib.matlab import figure, close, axes, subplot, show
from matplotlib.numerix import arange, sin, pi

t = arange(0.0, 1.0, 0.01)

figure(1)

ax1 = subplot(211)
plot(t, sin(2*pi*t))
grid(True)
ax1.set_ylim( (-2,2) )
ylabel('1 Hz')
title('A sine wave or two')

for label in ax1.get_xticklabels():
    label.set_color('r')


ax2 = fig.add_subplot(212)
ax2.plot(t, sin(2*2*pi*t))
ax2.grid(True)
ax2.set_ylim( (-2,2) )
l = ax2.set_xlabel('Hi mom')
l.set_color('g')
l.set_fontsize('large')

show()        


