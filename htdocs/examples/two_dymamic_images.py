#!/usr/bin/env python
"""
An animated image
"""
import sys, time, os, gc
from matplotlib import rcParams

from matplotlib.matlab import *
import gtk

# if hold is on the axes images will accumulate and your performance
# will tank!
rc('axes', hold=False)

class HandleDraws:
    drawing_idle_id = 0
    shape = 100,100  # image size
    cnt = 0
    def __init__(self):
        self.fig = figure(1)
        self.a1 = subplot(211)
        self.a2 = subplot(212)
        
    def idle_update(self, *args):
        'only call a draw if gtk is idle'
        if self.cnt==0: self.tstart = time.time()
        draw()
        self.drawing_idle_id = 0
        self.cnt += 1
        if self.cnt>=50:
            print 'FPS', self.cnt/(time.time() - self.tstart)
            sys.exit()
            
        return False

    def update1(self, data):
        if self.drawing_idle_id == 0:
            self.a1.imshow(data, interpolation='nearest')
            self.drawing_idle_id = gtk.idle_add(self.idle_update)
        else: print 'dropping frame for axes 1'
    def update2(self, data):
        if self.drawing_idle_id == 0:
            self.a2.imshow(data, interpolation='nearest')
            self.drawing_idle_id = gtk.idle_add(self.idle_update)
        else: print 'dropping frame for axes 2'
handler = HandleDraws()

def generate_events(*args):
    data = rand(100,100)

    # randomly pick which axes to update
    if rand()>0.5: handler.update1(data)
    else:          handler.update2(data)
    return True

cnt = 0

gtk.timeout_add(10, generate_events)
show()
