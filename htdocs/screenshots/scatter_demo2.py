from pylab import *
from data_helper import get_daily_data

intc, msft = get_daily_data()

delta1 = diff(intc.open)/intc.open[0]

# size in points ^2
volume = (15*intc.volume[:-2]/intc.volume[0])**2
close = 0.003*intc.close[:-2]/0.003*intc.open[:-2]
scatter(delta1[:-1], delta1[1:], c=close, s=volume, alpha=0.75)

ticks = arange(-0.06, 0.061, 0.02) 
xticks(ticks)
yticks(ticks)

xlabel(r'$\Delta_i$', fontsize=20)
ylabel(r'$\Delta_{i+1}$', fontsize=20)
title('Volume and percent change')
grid(True)

show()


