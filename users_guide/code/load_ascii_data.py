from pylab import *
X = load('../data/ascii_data.dat')
t = X[:,0]  # the first column
s = X[:,1]  # the second row
plot(t, s, 'o')
