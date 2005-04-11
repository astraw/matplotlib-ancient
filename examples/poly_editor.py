"""
This is an example to show how to build cross-GUI applications using
matplotlib event handling to interact with objects on the canvas

"""
from matplotlib.artist import Artist
from matplotlib.patches import Polygon
from matplotlib.numerix import sqrt, nonzero, equal, asarray, dot, Float
from matplotlib.numerix.mlab import amin
from matplotlib.mlab import dist_point_to_segment



        
class PolygonInteractor:
    """
    An polygon editor.

    Key-bindings

      't' toggle vertex markers on and off.  When vertex markers are on,
          you can move them, delete them

      'd' delete the vertex under point      

      'i' insert a vertex at point.  You must be within epsilon of the
          line connecting two existing vertices
          
    """

    showverts = True
    epsilon = 5  # max pixel distance to count as a vertex hit

    def __init__(self, poly):
        if poly.figure is None:
            raise RuntimeError('You must first add the polygon to a figure or canvas before defining the interactor')
        canvas = poly.figure.canvas
        self.poly = poly
        self.poly.verts = list(self.poly.verts)
        x, y = zip(*self.poly.verts)
        self.line = Line2D(x,y,marker='o', markerfacecolor='r')
        #self._update_line(poly)
        
        cid = self.poly.add_callback(self.poly_changed)
        self._ind = None # the active vert

        canvas.mpl_connect('button_press_event', self.button_press_callback)
        canvas.mpl_connect('key_press_event', self.key_press_callback)        
        canvas.mpl_connect('button_release_event', self.button_release_callback)
        canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)                
        self.canvas = canvas
        

    def poly_changed(self, poly):
        'this method is called whenever the polygon object is called'
        # only copy the artist props to the line (except visibility)
        vis = self.line.get_visible()
        Artist.update_from(self.line, poly)
        self.line.set_visible(vis)  # don't use the poly visibility state
        

    def get_ind_under_point(self, event):
        'get the index of the vertex under point if within epsilon tolerance'
        x, y = zip(*self.poly.verts)
        
        # display coords        
        xt, yt = self.poly.get_transform().numerix_x_y(x, y)
        d = sqrt((xt-event.x)**2 + (yt-event.y)**2)
        indseq = nonzero(equal(d, amin(d)))
        ind = indseq[0]

        if d[ind]>=self.epsilon:
            ind = None

        return ind
        
    def button_press_callback(self, event):
        'whenever a mouse button is pressed'
        if not self.showverts: return 
        if event.inaxes==None: return
        if event.button != 1: return
        self._ind = self.get_ind_under_point(event)

    def button_release_callback(self, event):
        'whenever a mouse button is released'
        if not self.showverts: return
        if event.button != 1: return
        self._ind = None

    def key_press_callback(self, event):
        'whenever a key is pressed'
        if not event.inaxes: return
        if event.key=='t':
            self.showverts = not self.showverts
            self.line.set_visible(self.showverts)
            if not self.showverts: self._ind = None
        elif event.key=='d':
            ind = self.get_ind_under_point(event)
            if ind is not None:
                self.poly.verts = [tup for i,tup in enumerate(self.poly.verts) if i!=ind]
                self.line.set_data(zip(*self.poly.verts))
        elif event.key=='i':            
            xys = self.poly.get_transform().seq_xy_tups(self.poly.verts)
            p = event.x, event.y # display coords
            for i in range(len(xys)-1):                
                s0 = xys[i]
                s1 = xys[i+1]
                d = dist_point_to_segment(p, s0, s1)
                if d<=self.epsilon:
                    self.poly.verts.insert(i+1, (event.xdata, event.ydata))
                    self.line.set_data(zip(*self.poly.verts))
                    break
                
            
        self.canvas.draw()

    def motion_notify_callback(self, event):
        'on mouse movement'
        if not self.showverts: return 
        if self._ind is None: return
        if event.inaxes is None: return
        if event.button != 1: return
        x,y = event.xdata, event.ydata
        self.poly.verts[self._ind] = x,y
        self.line.set_data(zip(*self.poly.verts))
        self.canvas.draw_idle()


from pylab import *





fig = figure()
circ = Circle((.5,.5),.5)




ax = subplot(111)
ax.add_patch(circ)
p = PolygonInteractor( circ)

ax.add_line(p.line)
ax.set_title('Click and drag a point to move it')
ax.set_xlim((0,1))
ax.set_ylim((0,1))
show()
