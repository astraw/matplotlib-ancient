#!/usr/bin/env python

import os, sys, time
import matplotlib
#matplotlib.interactive(True)
#matplotlib.use('Cairo')
matplotlib.use('Agg')
from pylab import *


def report_memory(i):
    pid = os.getpid()
    a2 = os.popen('ps -p %d -o rss,sz' % pid).readlines()
    print i, '  ', a2[1],
    return int(a2[1].split()[1])



# take a memory snapshot on indStart and compare it with indEnd

indStart, indEnd = 30, 201
for i in range(indEnd):

    figure(1); clf()

    subplot(221)
    t1 = arange(0.0, 2.0, 0.01)
    y = sin(2*pi*t1)
    plot(t1,y,'-')
    plot(t1, rand(len(t1)), 's', hold=True)


    subplot(222)
    X = rand(50,50)

    imshow(X)
    subplot(223)
    scatter(rand(50), rand(50), s=100*rand(50), c=rand(50))
    subplot(224)
    pcolor(10*rand(50,50))
    #ion()
    #draw()

    #ioff()

    #fd = file('tmp%d' % i, 'wb')
    #savefig(fd, dpi = 75)
    #fd.close()
    savefig('tmp%d' % i, dpi = 75)
    close(1)
    #break

    val = report_memory(i)
    if i==indStart: start = val # wait a few cycles for memory usage to stabilize

end = val
print 'Average memory consumed per loop: %1.4fk bytes\n' % ((end-start)/float(indEnd-indStart))

"""
Average memory consumed per loop: 0.0053k bytes
"""
