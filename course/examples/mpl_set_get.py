from pylab import *
x = rand(20); y = rand(20)
lines = plot(x,y,'o')
type(lines)
len(lines)
savefig('../fig/mpl_set_get1')


set(lines, markerfacecolor='green', markeredgecolor='red',
    markersize=20, markeredgewidth=3, linestyle='--', linewidth=3)
t = xlabel('time (s)')
set(t, fontsize=20, color='darkslategray') 
savefig('../fig/mpl_set_get2')
