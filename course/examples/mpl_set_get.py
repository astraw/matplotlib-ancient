from pylab import *
x = rand(20); y = rand(20)
lines = plot(x,y,'o')
type(lines)        # plot always returns a list
len(lines)         # even if it is lenght 1
savefig('../fig/mpl_set_get1')

get(lines)
set(lines)
set(lines, markerfacecolor='green', markeredgecolor='red',
    markersize=20, markeredgewidth=3, linestyle='--', linewidth=3)
t = xlabel('time (s)')
set(t, fontsize=20, color='darkslategray') 
savefig('../fig/mpl_set_get2')
