# For detailed comments on animation and the techniqes used here, see
# the wiki entry
# http://www.scipy.org/wikis/topical_software/MatplotlibAnimation
import matplotlib
matplotlib.use('TkAgg')

import sys
import pylab as p
import matplotlib.numerix as nx
import time

ax = p.subplot(111)
canvas = ax.figure.canvas


# create the initial line
x = nx.arange(0,2*nx.pi,0.01)
line, = p.plot(x, nx.sin(x), animated=True, lw=2)

def run(*args):
    background = canvas.copy_from_bbox(ax.bbox)
    # for profiling
    tstart = time.time()

    while 1:
        # restore the clean slate background
        canvas.restore_region(background)
        # update the data
        line.set_ydata(nx.sin(x+run.cnt/10.0))  
        # just draw the animated artist
        ax.draw_artist(line)
        # just redraw the axes rectangle
        canvas.blit(ax.bbox) 

        if run.cnt==200:
            # print the timing info and quit
            print 'FPS:' , 200/(time.time()-tstart)
            sys.exit()

        run.cnt += 1
run.cnt = 0        


manager = p.get_current_fig_manager()
manager.window.after(100, run)

p.show()



