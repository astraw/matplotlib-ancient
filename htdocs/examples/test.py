import matplotlib
matplotlib.use('WX')
matplotlib.interactive(True)

from matplotlib.matlab import *
plot([1,2,3,4])
xlabel('time')
#savefig('test')
show()

