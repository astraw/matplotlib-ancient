from matplotlib import mlab
from pylab import figure, show
import matplotlib.cbook as cbook

datafile = cbook.get_sample_data('msft.csv', asfileobj=False)
print 'loading', datafile
a = mlab.csv2rec(datafile)
a.sort()
print a.dtype

fig = figure()
ax = fig.add_subplot(111)
ax.plot(a.date, a.adj_close, '-')
fig.autofmt_xdate()

# if you have xlwt installed, you can output excel
import mpl_toolkits.exceltools as exceltools
exceltools.rec2excel(a, 'test.xls')
show()
