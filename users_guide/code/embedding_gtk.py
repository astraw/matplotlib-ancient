#!/usr/bin/env python
from matplotlib.numerix import arange, sin, pi

import matplotlib            # specify your 
matplotlib.use('GTKAgg')     # backend 
import matplotlib.backends as backend
from backend.backend_gtkagg \
     import FigureCanvasGTKAgg 
from matplotlib.backends.backend_gtk \
     import NavigationToolbar2GTK 

from matplotlib.figure import Figure

import gtk

# set up your native GUI window
win = gtk.Window()
win.show()
win.connect("destroy", gtk.mainquit)

vbox = gtk.VBox(spacing=3)
vbox.show()
win.add(vbox)

# create a matplotlib figure - backend independent
# code here
fig = Figure()
ax = fig.add_subplot(111)
t = arange(0.0,3.0,0.01)
s = sin(2*pi*t)
ax.plot(t,s)

# the FigureCanvas classes are imbeddable in your GUI
# FigureCanvasGTKAgg derives from gtk.DrawingArea
canvas = FigureCanvasGTKAgg(fig)  
canvas.show()
vbox.pack_start(canvas)

# you can build a custom toolbar
toolbar = NavigationToolbar2GTK(canvas)
toolbar.show()
vbox.pack_start(toolbar, gtk.FALSE, gtk.FALSE)

gtk.main()
