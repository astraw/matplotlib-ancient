
from pylab import *

def press(event):
    x = rand()
    y = rand()
    text(x,y,event.key)
    draw()
    
connect('key_press_event', press)

plot(rand(12), rand(12), 'go')
show()
