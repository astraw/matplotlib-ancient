#!/usr/bin/env python
import pylab as P

#
# The hist() function now has a lot more options
#

#
# first create a single histogram
#
mu, sigma = 200, 25
x = mu + sigma*P.randn(10000)

# the histogram of the data with histtype='step'
n, bins, patches = P.hist(x, 50, normed=1, histtype='step')
P.setp(patches, 'facecolor', 'g', 'alpha', 0.75)

# add a line showing the expected distribution
y = P.normpdf( bins, mu, sigma)
l = P.plot(bins, y, 'k--', linewidth=1.5)


#
# create a histogram by providing the bin edges (unequally spaced)
#
P.figure()

bins = [100,125,150,160,170,180,190,200,210,220,230,240,250,275,300]
# the histogram of the data with histtype='step'
n, bins, patches = P.hist(x, bins, normed=1, histtype='bar', rwidth=0.8)

#
# now we create a cumulative histogram of the data
#
P.figure()

n, bins, patches = P.hist(x, 50, normed=1, histtype='step', cumulative=True)
P.setp(patches, 'facecolor', 'b', 'alpha', 0.75)

# add a line showing the expected distribution
y = P.normpdf( bins, mu, sigma).cumsum()
y /= y[-1]
l = P.plot(bins, y, 'k--', linewidth=1.5)

# create a second data-set with a smaller standard deviation
sigma2 = 15.
x = mu + sigma2*P.randn(10000)

n, bins, patches = P.hist(x, bins=bins, normed=1, histtype='step', cumulative=True)
P.setp(patches, 'facecolor', 'r', 'alpha', 0.5)

# add a line showing the expected distribution
y = P.normpdf( bins, mu, sigma2).cumsum()
y /= y[-1]
l = P.plot(bins, y, 'r--', linewidth=1.5)

P.grid(True)
P.ylim(0, 1.05)


#
# histogram has the ability to plot multiple data in parallel ...
#
P.figure()

# create a new data-set
x = mu + sigma*P.randn(1000,3)

n, bins, patches = P.hist(x, 10, normed=1, histtype='bar')

#
# ... or we can stack the data
#
P.figure()

n, bins, patches = P.hist(x, 10, normed=1, histtype='barstacked')


P.show()