from matplotlib.matlab import *

t = arange(0, 2.1, 0.1)
a = subplot(111)
plot(t, t**2, '-')
title('A really silly plot')
xaxis, yaxis = a.get_xaxis(), a.get_yaxis()
xgrid = xaxis.get_gridlines()
print len(xgrid) 
for line in xgrid:
    line.set_color('r')
    line.set_linewidth(3)

labels = xaxis.get_ticklabels()
for label in labels:
    label.set_fontname('Courier')
    label.set_fontsize(12)
    label.set_color('y')
    

show()
