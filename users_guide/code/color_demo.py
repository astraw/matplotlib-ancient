from pylab import *

# axis background in dark slate gray
subplot(111, axisbg=(0.1843, 0.3098, 0.3098))
t = arange(0.0, 1.0, 0.01)
s = sin(2*2*pi*t)

# yellow circles with red edge color
plot(t, s, 'yo', markeredgecolor='r')                     
xlabel('time (s)', color='b')       # xlabel is blue
ylabel('voltage (mV)', color=0.5)   # ylabel is light gray
title("Don't try this at home, folks", color='#afeeee')

savefig('../figures/color_demo.eps')
savefig('../figures/color_demo.png')

show()
