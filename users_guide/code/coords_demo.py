# Connect to the mouse move event and print the location of the mouse
# in data coordinates if the mouse is over an axes
from matplotlib.matlab import *

plot(arange(10))

def on_move(event):
    # get the x and y pixel coords
    x, y = event.x, event.y

    if event.inaxes:
        print 'data coords', event.xdata, event.ydata

mpl_connect('motion_notify_event', on_move)


show()
