# Thanks to Charles Twardy for this example
#
#See http://matplotlib.sf.net/examples/legend_demo2.py for an example
#controlling which lines the legend uses and the order

from pylab import *

a = arange(0,3,.02)
b = arange(0,3,.02)
c = exp(a)
d = c.tolist()
d.reverse()
d = array(d)

ax = subplot(111)
plot(a,c,'k--',a,d,'k:',a,c+d,'k')
legend(('Model length', 'Data length', 'Total message length'),
       'upper center', shadow=True)
ax.set_ylim([-1,20])
ax.grid(0)
xlabel('Model complexity --->')
ylabel('Message length --->')
title('Minimum Message Length')
ax.set_xticklabels([])
ax.set_yticklabels([])
show()



