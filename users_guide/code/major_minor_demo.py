from pylab import *
# import the tick locator and formatter classes
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

majorLocator   = MultipleLocator(20)       # multiples of 20
majorFormatter = FormatStrFormatter('%d')  # integer format string
minorLocator   = MultipleLocator(5)        # multiples of 5

# my favorite plot!
t = arange(0.0, 100.0, 0.1)
s = sin(0.1*pi*t)*exp(-t*0.01)

ax = subplot(111)
plot(t,s)

# now just set the major and minor locators and formatters
ax.xaxis.set_major_locator(majorLocator)
ax.xaxis.set_major_formatter(majorFormatter)

#for the minor ticks, use no labels; default NullFormatter
ax.xaxis.set_minor_locator(minorLocator) 

savefig('../figures/major_minor_demo.eps')
savefig('../figures/major_minor_demo.png')

show()
