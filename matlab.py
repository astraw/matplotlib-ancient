"""
This is a matlab style functional interface the matplotlib.

The following matlab compatible commands are provided

Plotting commands

  axes     - Create a new axes
  axis     - Set or return the current axis limits
  bar      - make a bar chart
  close    - close a figure window
  errorbar - make an errorbar graph
  figure   - create or change active figure
  gca      - return the current axes
  gcf      - return the current figure
  get      - get a handle graphics property
  hist     - make a histogram
  plot     - make a line plot
  savefig  - save the current figure
  scatter  - make a scatter plot
  set      - set a handle graphics property
  show     - show the figures
  subplot  - make a subplot (numrows, numcols, axesnum)
  text     - add some text at location x,y to the current axes
  title    - add a title to the current axes
  xlabel   - add an xlabel to the current axes
  ylabel   - add a ylabel to the current axes

Matrix commands

  cumprod   - the cumulative product along a dimension
  cumsum    - the cumulative sum along a dimension
  detrend   - remove the mean or besdt fit line from an array
  diag      - the k-th diagonal of matrix 
  diff      - the n-th differnce of an array
  eig       - the eigenvalues and eigen vectors of v
  eye       - a matrix where the k-th diagonal is ones, else zero 
  find      - return the indices where a condition is nonzero  
  fliplr    - flip the rows of a matrix up/down
  flipud    - flip the columns of a matrix left/right
  linspace  - a linear spaced vector of N values from min to max inclusive
  ones      - an array of ones
  rand      - an array from the uniform distribution [0,1]
  randn     - an array from the normal distribution
  rot90     - rotate matrix k*90 degress counterclockwise
  squeeze   - squeeze an array removing any dimensions of length 1
  tri       - a triangular matrix
  tril      - a lower triangular matrix
  triu      - an upper triangular matrix
  vander    - the Vandermonde matrix of vector x
  svd       - singular value decomposition
  zeros     - a matrix of zeros
  
Probability

  levypdf   - The levy probability density function from the char. func.
  normpdf   - The Gaussian probability density function
  pdffit    - First data to a probability density function
  rand      - random numbers from the uniform distribution
  randn     - random numbers from the normal distribution

Statistics

  corrcoef  - correlation coefficient
  cov       - covariance matrix
  max       - the maximum along dimension m
  mean      - the mean along dimension m
  median    - the median along dimension m
  min       - the minimum along dimension m
  norm      - the norm of vector x
  prod      - the product along dimension m
  ptp       - the max-min along dimension m
  std       - the standard deviation along dimension m
  sum       - the sum along dimension m

Time series analysis

  bartlett  - M-point Bartlett window
  blackman  - M-point Blackman window
  cohere    - the coherence using average periodiogram
  csd       - the cross spectral density using average periodiogram
  fft       - the fast Fourier transform of vector x
  hamming   - M-point Hamming window
  hanning   - M-point Hanning window
  hist      - compute the histogram of x
  kaiser    - M length Kaiser window
  psd       - the power spectral density using average periodiogram
  sinc      - the sinc function of array x

Other

  angle     - the angle of a complex array
  polyfit   - fit x, y to an n-th order polynomial
  polyval   - evaluate an n-th order polynomial
  roots     - the roots of the polynomial coefficients in p
  trapz     - trapezoidal integration


Credits: The plotting commands were provided by
John D. Hunter <jdhunter@ace.bsd.uhicago.edu>

Most of the other commands are from the Numeric, MLab and FFT, with
the exception of those in mlab.py provided by matplotlib.
"""

# bring all the MLab and mlab symbols in so folks can import them from
# matplotlib.matlab in one fell swoop
from Numeric import *
from MLab import *
from mlab import *
from FFT import fft

import pygtk
pygtk.require('2.0')
import gtk
from gtk import gdk

from gtkutils import error_msg, raise_msg_to_str
from cbook import is_string_like, flatten
from figure import Figure, Subplot, Axes, to_arrays, NavigationToolbar
import mlab  #so I can override hist, psd, etc...

interactive =0


def plotting():
    """
    Plotting commands

    axes     - Create a new axes
    axis     - Set or return the current axis limits
    bar      - make a bar chart
    close    - close a figure window
    errorbar - make an errorbar graph
    figure   - create or change active figure
    gca      - return the current axes
    gcf      - return the current figure
    get      - get a handle graphics property
    hist     - make a histogram
    plot     - make a line plot
    savefig  - save the current figure
    scatter  - make a scatter plot
    set      - set a handle graphics property
    show     - show the figures
    subplot  - make a subplot (numrows, numcols, axesnum)
    text     - add some text at location x,y to the current axes
    title    - add a title to the current axes
    xlabel   - add an xlabel to the current axes
    ylabel   - add a ylabel to the current axes
    """
    pass

def get_plot_commands():
    return ['axis', 'axes', 'subplot', 'plot', 'set', 'get', 'title',
     'xlabel', 'ylabel', 'text', 'scatter', 'errorbar', 'bar', 'hist',
     'figure', 'gca', 'gcf', 'close' ]

def draw_if_interactive():
    #print 'interactive', interactive
    if interactive:
        gcf().draw()
        
class FigureWin:
    def __init__(self, figure, window, vbox, toolbar):
        self.figure = figure
        self.window = window
        self.vbox = vbox
        self.toolbar = toolbar
        self.axes = {}

    def add_subplot(self, *args):
        if self.axes.has_key(args):
            self.currentAxis = self.axes[args]
        else:
            a = Subplot(*args)
            self.figure.add_axis(a)
            self.toolbar.update()
            self.axes[args] = a
            self.currentAxis = a
            return a
        
    def add_axes(self, rect, axisbg):
        rect = tuple(rect)
        if self.axes.has_key(rect):
            self.currentAxis = self.axes[rect]
        else:
            a = Axes(position=rect, axisbg=axisbg)
            self.figure.add_axis(a)
            self.axes[rect] = a
            self.currentAxis = a
            return a
    def get_current_axis(self):
        try: return self.currentAxis
        except AttributeError:
            self.add_subplot(111)
            return self.currentAxis

    def set_current_axes(self, a):
        if a not in self.axes.values():
            error_msg('Axes is not in current figure')
        self.currentAxis = a


        
        
    
        


class Gcf:
    __shared_state = {}
    figs = {}
    lastActive = None   # todo: last active needs to be a stack
    active = None
    def __init__(self, num=None):
        self.__dict__ = self.__shared_state

        if num is None and self.active is not None:
            # nothing to do
            return
        
        if self.figs.has_key(num): active = self.figs[num]
        else: active = self.newfig(num)
            
        if active!=self.active:
            self.lastActive, self.active = self.active, active
            

    def destroy(self, num):
        if not self.has_fignum(num): return
        self.figs[num].window.destroy()
        self.active = self.lastActive
        
    def has_fignum(num):
        return self.figs.has_key(num)
            
    def get_current_figwin(self):
        if self.active is not None: return self.active
        else: return self.newfig()
            
    def newfig(self, num=None):
        if num is None:
            if len(self.figs)>0:
                num = max(self.figs.keys())+1
            else:
                num = 1
        thisFig = Figure(size=(600,400))
        thisFig.show()
        win = gtk.Window()
        win.set_title("Figure %d" % num)
        win.connect("destroy", lambda *args: win.destroy())
        win.set_border_width(5)

        vbox = gtk.VBox(spacing=3)
        win.add(vbox)
        vbox.show()
        vbox.pack_start(thisFig)


        toolbar = NavigationToolbar( thisFig, win)
        toolbar.show()
        vbox.pack_start(toolbar, gtk.FALSE, gtk.FALSE )
        figwin = FigureWin(thisFig, win, vbox, toolbar)
        self.figs[num] = figwin
        win.show()
        return figwin


def gcf():
    "Return a handle to the current figure"
    return Gcf().get_current_figwin().figure

def figure(num=1):
    """
    Create a new figure and return a handle to it

    If figure(num) already exists, make it active and return the
    handle to it.    
    """
    if num==0:
        error_msg('Figure number can not be 0.\n' + \
                  'Hey, give me a break, this is matlab compatability')
        return 
    return Gcf(num).get_current_figwin().figure
    
def close(num=1):
    "Close the figure window num"
    Gcf().destroy(num)

def gca():
    """
    Return the current axis instance.  This can be used to control
    axis properties either using set or the Axes methods.

    Example:

      plot(t,s)
      set(gca(), 'xlim', [0,10])  # set the x axis limits

    or

      plot(t,s)
      a = gca()
      a.set_xlim([0,10])          # does the same
    """

    return Gcf().get_current_figwin().get_current_axis()

def axis(*v):
    """
    axis() returns the current axis as a length a length 4 vector

    axis(v) where v= [xmin xmax ymin ymax] sets the min and max of the
    x and y axis limits
    """
    
    try: v[0]
    except IndexError:
        xlim = gca().get_xlim()
        ylim = gca().get_ylim()
        return [xlim[0], xlim[1], ylim[0], ylim[1]]
    
    v = v[0]
    if len(v) != 4:
        error_msg('v must contain [xmin xmax ymin ymax]')
        return 
    gca().set_xlim([v[0], v[1]])
    gca().set_ylim([v[2], v[3]])
    draw_if_interactive()
    
def axes(*args, **kwargs):
    """
    Add an axis at positon rect specified by

      axes() by itself creates a default full window axis

      axes(rect, axisbg='w') where rect=[left, bottom, width, height] in
        normalized (0,1) units background is the background color for
        the axis, default white

      axes(h, axisbg='w') where h is an axes instance makes h the
        current axis An Axes instance is returned

    axisbg is a color format string which sets the background color of
    the axes (default white)
    """

    nargs = len(args)
    if args==0: return subplot(111)
    if nargs>1:
        error_msg('Only one non keyword arg to axes allowed')

    arg = args[0]

    if isinstance(arg, Axes):
        Gcf().get_current_figwin().set_current_axes(arg)
        return arg
    else:
        rect = arg
        return Gcf().get_current_figwin().add_axes(
            rect=rect, **kwargs)

def bar(*args, **kwargs):
    """
    bar(self, x, y, width=0.8)

    Make a bar plot with rectangles at x, x+width, 0, y
    x and y are Numeric arrays

    Return value is a list of Rectangle patch instances
    """

    try: patches =  gca().bar(*args, **kwargs)
    except ValueError, msg:
        msg = raise_msg_to_str(msg)
        error_msg(msg)
        raise RuntimeError, msg
    draw_if_interactive()
    return patches

def errorbar(x, y, e, u=None, fmt='b-'):
    """

    Plot x versus y with error bars in e.  if u is not None, then u
    gives the upper error bars and e gives the lower error bars.
    Otherwise e the error bars are symmetrix about y and given in the
    array e.
    
    fmt is the plot format symbol for y

    Return value is a length 2 tuple.  The first element is a list of
    y symbol lines.  The second element is a list of error bar lines.
    
    """
    
    l0 = plot(x,y,fmt)

    e = to_arrays(Float, e)
    if u is None: u = e
    upper = y+u
    lower = y-e
    width = (max(x)-min(x))*0.005
    a = gca()
    try: 
        l1 = a.vlines(x, y, lower)
        l2 = a.vlines(x, y, upper)
        l3 = a.hlines(upper, x-width, x+width)
        l4 = a.hlines(lower, x-width, x+width)
    except ValueError, msg:
        msg = raise_msg_to_str(msg)
        error_msg(msg)
        raise RuntimeError, msg
    
    l1.extend(l2)
    l3.extend(l4)
    l1.extend(l3)
    draw_if_interactive()
    return (l0, l1)



def get(o, s):
    """
    Return the value of handle property s

    h is an instance of a class, eg a Line2D or an Axes or AxisText.
    if s is 'somename', this function returns

      o.get_somename()
    
    """
    func = 'o.get_%s(val)' % s
    return eval(func, {}, {'o': o})


def plot(*args, **kwargs):
    """
    plot lines.  *args is a variable length argument, allowing for
    multiple x, y pairs with an optional format string.  For
    example, all of the following are legal
        
      plot(x,y)            # plot Numeric arrays y vs x
      plot(x,y, 'bo')      # plot Numeric arrays y vs x with blue circles
      plot(y)              # plot y using x = arange(len(y))
      plot(y, 'r+')        # ditto with red plusses

    An arbitrary number of x, y, fmt groups can be specified, as in 

      a.plot(x1, y1, 'g^', x2, y2, 'l-')  

    Return value is a list of lines that were added

    The following line styles are supported:

      -  : solid line
      -- : dashed line
      -. : dash-dot line
      :  : dotted line
      |  : verical lines
      .  : points
      ,  : pixels
      o  : circle symbols
      ^  : triangle up symbols
      v  : triangle down symbols
      <  : triangle left symbols
      >  : triangle right symbols
      s  : square symbols
      +  : plus symbols

    The following color strings are supported

      b  : blue
      g  : green
      r  : red
      c  : cyan
      m  : magenta
      y  : yellow
      k  : black 
      w  : white

   Line styles and colors are combined in a single format string
   

    """
    
    try: lines =  gca().plot(*args, **kwargs)
    except ValueError, msg:
        msg = raise_msg_to_str(msg)
        error_msg(msg)
    draw_if_interactive()
    return lines

def hist(x, bins=10, noplot=0, normed=0):
    """
    Compute the histogram of x.  bins is either an integer number of
    bins or a sequence giving the bins.  x are the data to be binned.

    if noplot is True, just compute the histogram and return the
    number of observations and the bins as an (n, bins) tuple.

    If noplot is False, compute the histogram and plot it, returning
    n, bins, patches

    If normed is true, the first element of the return tuple will be the
    counts normalized to form a probability distribtion, ie,
    n/(len(x)*dbin)
    
    """
    n,bins = mlab.hist(x, bins, normed)
    width = bins[1]-bins[0]
    if noplot: return n, bins
    else:
        try:
            patches = gca().bar(bins, n, width=width)
        except ValueError, msg:
            msg = raise_msg_to_str(msg)
            error_msg(msg)
            raise RuntimeError, msg
    draw_if_interactive()
    return n, bins, patches

    

def hlines(*args, **kwargs):    
    """
    lines = hlines(self, y, xmin, xmax, fmt='k-')

    plot horizontal lines at each y from xmin to xmax.  xmin or
    xmax can be scalars or len(x) numpy arrays.  If they are
    scalars, then the respective values are constant, else the
    widths of the lines are determined by xmin and xmax

    Returns a list of line instances that were added

    """
    try: lines =  gca().hlines(*args, **kwargs)
    except ValueError, msg:
        msg = raise_msg_to_str(msg)
        error_msg(msg)
        raise RuntimeError, msg
    draw_if_interactive()
    return lines



def savefig(fname, size=(800,600)):
    """
    Save the current figure to filename fname.  size is a (width, height)
    tuple giving the figure resolution in pixels.

    Output file types currently supported are jpeg and png and will be
    deduced by the extension to fname
    
    """
    # print_figure does it's own error handling because of queing
    gcf().print_figure(fname, size)

def scatter(*args, **kwargs):
    """

    scatter(self, x, y, s=None, c='b'):

    Make a scatter plot of x versus y.  s is a size (in data
    coords) and can be either a scalar or an array of the same
    length as x or y.  c is a color and can be a single color
    format string or an length(x) array of intensities which will
    be mapped by the colormap jet.        

    If size is None a default size will be used
    """

    try: patches =  gca().scatter(*args, **kwargs)
    except ValueError, msg:
        msg = raise_msg_to_str(msg)
        error_msg(msg)
        raise RuntimeError, msg
    draw_if_interactive()
    return patches

def set(h, s, val):
    """
    Set handle h property in string s to value val

    h can be a handle or vector of handles.

    h is an instance (or vector of instances) of a class, eg a Line2D
    or an Axes or AxisText.  if s is 'somename', this function calls

      o.set_somename(val)

    for every instance in o in h
    """
    if not iterable(h): h = [h]
    else: h = flatten(h)
    for o in h:
        try: 
            func = 'o.set_%s(val)' % s
            eval(func, {}, {'o': o, 'val' : val})
        except ValueError, msg:
            msg = raise_msg_to_str(msg)
            error_msg(msg)
            raise RuntimeError, msg
    draw_if_interactive()

def show():
    """
    Show all the figures and enter the gtk mainloop

    This should be the last line of your script
    """
    if not interactive:
        gtk.mainloop()

def subplot(*args):
    """
    Create a subplot command, creating axes with

      subplot(numRows, numCols, plotNum)

    where plotNum=1 is the first plot number and increasing plotNums
    fill rows first.  max(plotNum)==numRows*numCols

    You can leave out the commas if numRows<=numCols<=plotNum<10, as
    in

      subplot(211)    # 2 rows, 1 column, first (upper) plot

    subplot(111) is the default axis
    """
    try:
        Gcf().get_current_figwin().add_subplot(*args)
        a =  gca()
    except ValueError, msg:
        msg = raise_msg_to_str(msg)
        error_msg(msg)
        raise RuntimeError, msg
    draw_if_interactive()
    return a

def text(x, y, label, *args, **kwargs):
    """
    Add text to axis at location x,y

    args, if present, must be a single argument which is a dictionary
    to override the default text properties.  If no dictionary is
    provided, this will be used

      'fontsize'            : 9,
      'verticalalignment'   : 'bottom',
      'horizontalalignment' : 'left'

    **kwargs can in turn be used to override the override, as in

      a.text(x,y,label, fontsize=12)

    This command supplies no override dict, and so will have
    'verticalalignment'='bottom' and 'horizontalalignment'='left' but
    the keyword arg 'fontsize' will create a fontsize of 12

    The purpose of all of these options is to make it easy for you to
    create a default font theme for your plots by creating a single
    dictionary, and then being able to selective change individual
    attributes for the varous text creation commands, as in

        fonts = {
          'color'               : 'k',
          'fontname'            : 'Courier',
          'fontweight'          : 'bold'
          }

        title('My title', fonts, fontsize=12)
        xlabel('My xlabel', fonts, fontsize=10)
        ylabel('My ylabel', fonts, fontsize=10)
        text(12, 20, 'some text', fonts, fontsize=8)

    The AxisText defaults are

        'color'               : 'k',
        'fontname'            : 'Sans',
        'fontsize'            : 10,
        'fontweight'          : 'bold',
        'fontangle'           : 'normal',
        'horizontalalignment' : 'left'
        'rotation'            : 'horizontal',
        'verticalalignment'   : 'bottom',

    """
    t =  gca().text(x, y, label, *args, **kwargs)
    draw_if_interactive()
    return t

def title(s, *args, **kwargs):
    """
    Set the title of the current axis to s

    Default font override is:
      override = {
        'fontsize'            : 11,
        'verticalalignment'   : 'bottom',
        'horizontalalignment' : 'center'
      }

    See the text docstring for information of how override and the
    optional args work

    """
    l =  gca().set_title(s, *args, **kwargs)
    draw_if_interactive()
    return l



def vlines(*args, **kwargs):    
    """
    lines =  vlines(x, ymin, ymax, color='k'):

    Plot vertical lines at each x from ymin to ymax.  ymin or ymax
    can be scalars or len(x) numpy arrays.  If they are scalars,
    then the respective values are constant, else the heights of
    the lines are determined by ymin and ymax

    Returns a list of lines that were added
    """
    try: lines =  gca().vlines(*args, **kwargs)
    except ValueError, msg:
        msg = raise_msg_to_str(msg)
        error_msg(msg)
        raise RuntimeError, msg
    draw_if_interactive()
    return lines

def xlabel(s, *args, **kwargs):
    """
    Set the x axis label of the current axis to s

    Default override is

      override = {
          'fontsize'            : 10,
          'verticalalignment'   : 'top',
          'horizontalalignment' : 'center'
          }

    See the text docstring for information of how override and
    the optional args work

    """
    l =  gca().set_xlabel(s, *args, **kwargs)
    draw_if_interactive()
    return l

def ylabel(s, *args, **kwargs):
    """
    Set the y axis label of the current axis to s

    Defaults override is

        override = {
           'fontsize'            : 10,
           'verticalalignment'   : 'center',
           'horizontalalignment' : 'right',
           'rotation'='vertical' : }

    See the text docstring for information of how override and the
    optional args work
    
    """
    l = gca().set_ylabel(s, *args, **kwargs)
    draw_if_interactive()
    return l
