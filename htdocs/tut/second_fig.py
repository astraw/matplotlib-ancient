from matplotlib.matlab import *
plot([1,2,3,4], [1,4,9,16], 'ro')
axis([0, 6, 0, 20])
savefig('secondfig.png', size=(300,250))
show()
