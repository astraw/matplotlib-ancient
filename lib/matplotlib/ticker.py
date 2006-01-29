"""
Tick locating and formatting
============================

This module contains classes to support completely configurable tick
locating and formatting.  Although the locators know nothing about
major or minor ticks, they are used by the Axis class to support major
and minor tick locating and formatting.  Generic tick locators and
formatters are provided, as well as domain specific custom ones..


Tick locating
-------------

The Locator class is the base class for all tick locators.  The
locators handle autoscaling of the view limits based on the data
limits, and the choosing of tick locations.  The most generally useful
tick locator is MultipleLocator.  You initialize this with a base, eg
10, and it picks axis limits and ticks that are multiples of your
base.  The class AutoLocator contains a MultipleLocator instance, and
dynamically updates it based upon the data and zoom limits.  This
should provide much more intelligent automatic tick locations both in
figure creation and in navigation than in prior versions of
matplotlib.

The basic generic  locators are

  * NullLocator     - No ticks

  * FixedLocator    - Tick locations are fixed

  * IndexLocator    - locator for index plots (eg where x = range(len(y))

  * LinearLocator   - evenly spaced ticks from min to max

  * LogLocator      - logarithmically ticks from min to max

  * MultipleLocator - ticks and range are a multiple of base;
                      either integer or float

  * AutoLocator     - choose a MultipleLocator and dyamically reassign
                      it for intelligent ticking during navigation

There are a number of locators specialized for date locations - see
the dates module

You can define your own locator by deriving from Locator.  You must
override the __call__ method, which returns a sequence of locations,
and you will probably want to override the autoscale method to set the
view limits from the data limits.

If you want to override the default locator, use one of the above or a
custom locator and pass it to the x or y axis instance.  The relevant
methods are::

  ax.xaxis.set_major_locator( xmajorLocator )
  ax.xaxis.set_minor_locator( xminorLocator )
  ax.yaxis.set_major_locator( ymajorLocator )
  ax.yaxis.set_minor_locator( yminorLocator )

The default minor locator is the NullLocator, eg no minor ticks on by
default.

Tick formatting
---------------

Tick formatting is controlled by classes derived from Formatter.  The
formatter operates on a single tick value and returns a string to the
axis.

  * NullFormatter      - no labels on the ticks

  * FixedFormatter     - set the strings manually for the labels

  * FuncFormatter      - user defined function sets the labels

  * FormatStrFormatter - use a sprintf format string

  * ScalarFormatter    - default formatter for scalars; autopick the fmt string

  * LogFormatter       - formatter for log axes


You can derive your own formatter from the Formatter base class by
simply overriding the __call__ method.  The formatter class has access
to the axis view and data limits.

To control the major and minor tick label formats, use one of the
following methods::

  ax.xaxis.set_major_formatter( xmajorFormatter )
  ax.xaxis.set_minor_formatter( xminorFormatter )
  ax.yaxis.set_major_formatter( ymajorFormatter )
  ax.yaxis.set_minor_formatter( yminorFormatter )

See examples/major_minor_demo1.py for an example of setting major an
minor ticks.  See the matplotlib.dates module for more information and
examples of using date locators and formatters.

DEVELOPERS NOTE

If you are implementing your own class or modifying one of these, it
is critical that you use viewlim and dataInterval READ ONLY MODE so
multiple axes can share the same locator w/o side effects!


"""


from __future__ import division
import sys, os, re, time, math, warnings
from mlab import linspace
from matplotlib import verbose, rcParams
from numerix import absolute, arange, array, asarray, Float, floor, log, \
     logical_and, nonzero, ones, take, zeros
from matplotlib.numerix.mlab import amin, amax, std, mean
from matplotlib.mlab import frange
from cbook import strip_math

class TickHelper:

    viewInterval = None
    dataInterval = None

    def verify_intervals(self):
        if self.dataInterval is None:
            raise RuntimeError("You must set the data interval to use this function")

        if self.viewInterval is None:
            raise RuntimeError("You must set the view interval to use this function")


    def set_view_interval(self, interval):
        self.viewInterval = interval

    def set_data_interval(self, interval):
        self.dataInterval = interval

class Formatter(TickHelper):
    """
    Convert the tick location to a string
    """

    # some classes want to see all the locs to help format
    # individual ones
    locs = []
    def __call__(self, x, pos=None):
        'Return the format for tick val x at position pos; pos=None indicated unspecified'
        raise NotImplementedError('Derived must overide')

    def format_data(self,value):
        return self.__call__(value)

    def get_offset(self):
        return ''

    def set_locs(self, locs):
        self.locs = locs

class NullFormatter(Formatter):
    'Always return the empty string'
    def __call__(self, x, pos=None):
        'Return the format for tick val x at position pos'
        return ''

class FixedFormatter(Formatter):
    'Return fixed strings for tick labels'
    def __init__(self, seq):
        """
        seq is a sequence of strings.  For positions i<len(seq) return
        seq[i] regardless of x.  Otherwise return ''
        """
        self.seq = seq

    def __call__(self, x, pos=None):
        'Return the format for tick val x at position pos'
        if pos is None or pos>=len(self.seq): return ''
        else: return self.seq[pos]

class FuncFormatter(Formatter):
    """
    User defined function for formatting
    """
    def __init__(self, func):
        self.func = func

    def __call__(self, x, pos=None):
        'Return the format for tick val x at position pos'
        return self.func(x, pos)


class FormatStrFormatter(Formatter):
    """
    Use a format string to format the tick
    """
    def __init__(self, fmt):
        self.fmt = fmt

    def __call__(self, x, pos=None):
        'Return the format for tick val x at position pos'
        return self.fmt % x


class OldScalarFormatter(Formatter):
    """
    Tick location is a plain old number.  If viewInterval is set, the
    formatter will use %d, %1.#f or %1.ef as appropriate.  If it is
    not set, the formatter will do str conversion
    """

    def __call__(self, x, pos=None):
        'Return the format for tick val x at position pos'
        self.verify_intervals()
        d = abs(self.viewInterval.span())

        return self.pprint_val(x,d)

    def pprint_val(self, x, d):
        #if the number is not too big and it's an int, format it as an
        #int
        if abs(x)<1e4 and x==int(x): return '%d' % x

        if d < 1e-2: fmt = '%1.3e'
        elif d < 1e-1: fmt = '%1.3f'
        elif d > 1e5: fmt = '%1.1e'
        elif d > 10 : fmt = '%1.1f'
        elif d > 1 : fmt = '%1.2f'
        else: fmt = '%1.3f'
        s =  fmt % x
        #print d, x, fmt, s
        tup = s.split('e')
        if len(tup)==2:
            mantissa = tup[0].rstrip('0').rstrip('.')
            sign = tup[1][0].replace('+', '')
            exponent = tup[1][1:].lstrip('0')
            s = '%se%s%s' %(mantissa, sign, exponent)
        else:
            s = s.rstrip('0').rstrip('.')
        return s


class ScalarFormatter(Formatter):
    """
    Tick location is a plain old number.  If useOffset==True and the data range
    is much smaller than the data average, then an offset will be determined
    such that the tick labels are meaningful. Scientific notation is used for
    data < 1e-3 or data >= 1e4.
    """
    def __init__(self, useOffset=True, useMathText=False):
        # useOffset allows plotting small data ranges with large offsets:
        # for example: [1+1e-9,1+2e-9,1+3e-9]
        # useMathText will render the offset an scientific notation in mathtext
        self._useOffset = useOffset
        self._useMathText = useMathText or rcParams['text.usetex']
        self.offset = 0
        self.orderOfMagnitude = 0
        self.format = ''

    def __call__(self, x, pos=None):
        'Return the format for tick val x at position pos'
        if len(self.locs)==0:
            return ''
        else:
            return self.pprint_val(x)

    def format_data(self,value):
        'return a formatted string representation of a number'
        s = '%1.4e'% value
        return self._formatSciNotation(s)

    def get_offset(self):
        """Return scientific notation, plus offset"""
        if len(self.locs)==0: return ''
        if self.orderOfMagnitude or self.offset:
            offsetStr = ''
            sciNotStr = ''
            if self.offset:
                p = ('+%1.10e'% self.offset).replace('+-','-')
                offsetStr = self._formatSciNotation(p,mathtext=self._useMathText)
            if self.orderOfMagnitude:
                if self._useMathText: sciNotStr = r'{\times}10^{%d}'% self.orderOfMagnitude
                else: sciNotStr = 'x1e%d'% self.orderOfMagnitude
            if self._useMathText: return ''.join(('$',sciNotStr,offsetStr,'$'))
            else: return ''.join((sciNotStr,offsetStr))
        else: return ''

    def set_locs(self, locs):
        'set the locations of the ticks'
        self.locs = locs
        if len(self.locs) > 0:
            self.verify_intervals()
            d = abs(self.viewInterval.span())
            if self._useOffset: self._set_offset(d)
            self._set_orderOfMagnitude(d)
            self._set_format()

    def _set_offset(self, range):
        # offset of 20,001 is 20,000, for example
        locs = self.locs

        if locs is None or not len(locs):
            self.offset = 0
        ave_loc = mean(locs)
        if ave_loc: # dont want to take log10(0)
            ave_oom = math.floor(math.log10(mean(absolute(locs))))
            range_oom = math.floor(math.log10(range))
            if absolute(ave_oom-range_oom) >= 3: # four sig-figs
                if ave_loc < 0:
                    self.offset = math.ceil(amax(locs)/10**range_oom)*10**range_oom
                else:
                    self.offset = math.floor(amin(locs)/10**(range_oom))*10**(range_oom)
            else: self.offset = 0

    def _set_orderOfMagnitude(self,range):
        # if scientific notation is to be used, find the appropriate exponent
        # if using an numerical offset, find the exponent after applying the offset
        locs = absolute(self.locs)
        if self.offset: oom = math.floor(math.log10(range))
        else:
            if locs[0] > locs[-1]: val = locs[0]
            else: val = locs[-1]
            if val == 0: oom = 0
            else: oom = math.floor(math.log10(val))
        if oom <= -3:
            self.orderOfMagnitude = oom
        elif oom >= 4:
            self.orderOfMagnitude = oom
        else:
            self.orderOfMagnitude = 0

    def _set_format(self):
        # set the format string to format all the ticklabels
        locs = (array(self.locs)-self.offset) / 10**self.orderOfMagnitude+1e-15
        sigfigs = [len(str('%1.3f'% loc).split('.')[1].rstrip('0')) \
                   for loc in locs]
        sigfigs.sort()
        self.format = '%1.' + str(sigfigs[-1]) + 'f'

    def pprint_val(self, x):
        xp = (x-self.offset)/10**self.orderOfMagnitude
        if absolute(xp) < 1e-8: xp = 0
        return self.format % xp

    def _formatSciNotation(self,s,mathtext=False):
        # transform 1e+004 into 1e4, for example
        tup = s.split('e')
        try:
            mantissa = tup[0].rstrip('0').rstrip('.')
            sign = tup[1][0].replace('+', '')
            exponent = tup[1][1:].lstrip('0')
            if mathtext:
                res = '%se{%s%s}' %(mantissa, sign, exponent)
                return res.replace('e{}','').replace('e',r'{\times}10^')
            else:
                return ('%se%s%s' %(mantissa, sign, exponent)).rstrip('e')
        except IndexError,msg:
            return s


class LogFormatter(Formatter):
    """
    Format values for log axis;

    if attribute decadeOnly is True, only the decades will be labelled.
    """
    def __init__(self, base=10.0, labelOnlyBase = True):
        """
        base is used to locate the decade tick,
        which will be the only one to be labeled if labelOnlyBase
        is False
        """
        self._base = base+0.0
        self.labelOnlyBase=labelOnlyBase
        self.decadeOnly = True

    def base(self,base):
        'change the base for labeling - warning: should always match the base used for LogLocator'
        self._base=base

    def label_minor(self,labelOnlyBase):
        'switch on/off minor ticks labeling'
        self.labelOnlyBase=labelOnlyBase


    def __call__(self, x, pos=None):
        'Return the format for tick val x at position pos'
        self.verify_intervals()
        d = abs(self.viewInterval.span())
        b=self._base
        # only label the decades
        fx = math.log(x)/math.log(b)
        isDecade = self.is_decade(fx)
        if not isDecade and self.labelOnlyBase: s = ''
        elif x>10000: s= '%1.0e'%x
        elif x<1: s =  '%1.0e'%x
        else        : s =  self.pprint_val(x,d)
        return s

    def format_data(self,value):
        self.labelOnlyBase = False
        value = strip_math(self.__call__(value))
        self.labelOnlyBase = True
        return value

    def is_decade(self, x):
        n = self.nearest_long(x)
        return abs(x-n)<1e-10

    def nearest_long(self, x):
        if x==0: return 0L
        elif x>0: return long(x+0.5)
        else: return long(x-0.5)

    def pprint_val(self, x, d):
        #if the number is not too big and it's an int, format it as an
        #int
        if abs(x)<1e4 and x==int(x): return '%d' % x

        if d < 1e-2: fmt = '%1.3e'
        elif d < 1e-1: fmt = '%1.3f'
        elif d > 1e5: fmt = '%1.1e'
        elif d > 10 : fmt = '%1.1f'
        elif d > 1 : fmt = '%1.2f'
        else: fmt = '%1.3f'
        s =  fmt % x
        #print d, x, fmt, s
        tup = s.split('e')
        if len(tup)==2:
            mantissa = tup[0].rstrip('0').rstrip('.')
            sign = tup[1][0].replace('+', '')
            exponent = tup[1][1:].lstrip('0')
            s = '%se%s%s' %(mantissa, sign, exponent)
        else:
            s = s.rstrip('0').rstrip('.')
        return s

class LogFormatterExponent(LogFormatter):
    """
    Format values for log axis; using exponent = log_base(value)
    """

    def __call__(self, x, pos=None):
        'Return the format for tick val x at position pos'
        self.verify_intervals()
        d = abs(self.viewInterval.span())
        b=self._base
        # only label the decades
        fx = math.log(x)/math.log(b)
        isDecade = self.is_decade(fx)
        if not isDecade and self.labelOnlyBase: s = ''
        #if 0: pass
        elif fx>10000: s= '%1.0e'%fx
        #elif x<1: s = '$10^{%d}$'%fx
        #elif x<1: s =  '10^%d'%fx
        elif fx<1: s =  '%1.0e'%fx
        else        : s =  self.pprint_val(fx,d)
        return s


class LogFormatterMathtext(LogFormatter):
    """
    Format values for log axis; using exponent = log_base(value)
    """

    def __call__(self, x, pos=None):
        'Return the format for tick val x at position pos'
        self.verify_intervals()

        b = self._base
        # only label the decades
        fx = math.log(x)/math.log(b)
        isDecade = self.is_decade(fx)


        if not isDecade and self.labelOnlyBase: s = ''
        elif not isDecade: s = '$%d^{%.2f}$'% (b, fx)
        else: s = '$%d^{%d}$'% (b, self.nearest_long(fx))

        return s




class Locator(TickHelper):
    """
    Determine the tick locations;

    Note, you should not use the same locator between different Axis
    because the locator stores references to the Axis data and view
    limits
    """

    def __call__(self):
        'Return the locations of the ticks'
        raise NotImplementedError('Derived must override')

    def autoscale(self):
        'autoscale the view limits'
        self.verify_intervals()
        return  self.nonsingular(*self.dataInterval.get_bounds())

    def pan(self, numsteps):
        'Pan numticks (can be positive or negative)'
        ticks = self()
        numticks = len(ticks)

        if numticks>2:
            step = numsteps*abs(ticks[0]-ticks[1])
        else:
            step = numsteps*self.viewInterval.span()/6

        self.viewInterval.shift(step)

    def zoom(self, direction):
        "Zoom in/out on axis; if direction is >0 zoom in, else zoom out"
        vmin, vmax = self.viewInterval.get_bounds()
        interval = self.viewInterval.span()
        step = 0.1*interval*direction
        self.viewInterval.set_bounds(vmin + step, vmax - step)

    def nonsingular(self, vmin, vmax, expander = 0.001):
        if vmax < vmin:
            vmin, vmax = vmax, vmin
        if vmin==vmax:
            if vmin==0.0:
                vmin -= 1
                vmax += 1
            else:
                vmin -= expander*abs(vmin)
                vmax += expander*abs(vmax)
        return vmin, vmax

    def refresh(self):
        'refresh internal information based on current lim'
        pass


class IndexLocator(Locator):
    """
    Place a tick on every multiple of some base number of points
    plotted, eg on every 5th point.  It is assumed that you are doing
    index plotting; ie the axis is 0, len(data).  This is mainly
    useful for x ticks.
    """
    def __init__(self, base, offset):
        'place ticks on the i-th data points where (i-offset)%base==0'
        self._base = base
        self.offset = offset

    def __call__(self):
        'Return the locations of the ticks'
        dmin, dmax = self.dataInterval.get_bounds()
        return arange(dmin + self.offset, dmax+1, self._base)


class FixedLocator(Locator):
    """
    Tick locations are fixed
    """

    def __init__(self, locs):
        self.locs = locs

    def __call__(self):
        'Return the locations of the ticks'
        return self.locs


class NullLocator(Locator):
    """
    No ticks
    """

    def __call__(self):
        'Return the locations of the ticks'
        return []

class LinearLocator(Locator):
    """
    Determine the tick locations

    The first time this function is called it will try to set the
    number of ticks to make a nice tick partitioning.  Thereafter the
    number of ticks will be fixed so that interactive navigation will
    be nice
    """


    def __init__(self, numticks = None, presets=None):
        """
        Use presets to set locs based on lom.  A dict mapping vmin, vmax->locs
        """
        self.numticks = numticks
        if presets is None:
            self.presets = {}
        else:
            self.presets = presets

    def __call__(self):
        'Return the locations of the ticks'

        self.verify_intervals()
        vmin, vmax = self.viewInterval.get_bounds()
        if vmax<vmin:
            vmin, vmax = vmax, vmin

        if self.presets.has_key((vmin, vmax)):
            return self.presets[(vmin, vmax)]

        if self.numticks is None:
            self._set_numticks()



        if self.numticks==0: return []
        ticklocs = linspace(vmin, vmax, self.numticks)

        return ticklocs


    def _set_numticks(self):
        self.numticks = 11  # todo; be smart here; this is just for dev

    def autoscale(self):
        'Try to choose the view limits intelligently'
        self.verify_intervals()
        vmin, vmax = self.dataInterval.get_bounds()

        if vmax<vmin:
            vmin, vmax = vmax, vmin

        if vmin==vmax:
            vmin-=1
            vmax+=1

        exponent, remainder = divmod(math.log10(vmax - vmin), 1)

        if remainder < 0.5:
            exponent -= 1
        scale = 10**(-exponent)
        vmin = math.floor(scale*vmin)/scale
        vmax = math.ceil(scale*vmax)/scale

        return self.nonsingular(vmin, vmax)


def closeto(x,y):
    if abs(x-y)<1e-10: return True
    else: return False

class Base:
    'this solution has some hacks to deal with floating point inaccuracies'
    def __init__(self, base):
        assert(base>0)
        self._base = base

    def lt(self, x):
        'return the largest multiple of base < x'
        d,m = divmod(x, self._base)
        if closeto(m,0) and not closeto(m/self._base,1):
            return (d-1)*self._base
        return d*self._base

    def le(self, x):
        'return the largest multiple of base <= x'
        d,m = divmod(x, self._base)
        if closeto(m/self._base,1): # was closeto(m, self._base)
            #looks like floating point error
            return (d+1)*self._base
        return d*self._base

    def gt(self, x):
        'return the smallest multiple of base > x'
        d,m = divmod(x, self._base)
        if closeto(m/self._base,1):
            #looks like floating point error
            return (d+2)*self._base
        return (d+1)*self._base

    def ge(self, x):
        'return the smallest multiple of base >= x'
        d,m = divmod(x, self._base)
        if closeto(m,0) and not closeto(m/self._base,1):
            return d*self._base
        return (d+1)*self._base

    def get_base(self):
        return self._base

class MultipleLocator(Locator):
    """
    Set a tick on every integer that is multiple of base in the
    viewInterval
    """

    def __init__(self, base=1.0):
        self._base = Base(base)

    def __call__(self):
        'Return the locations of the ticks'

        self.verify_intervals()

        vmin, vmax = self.viewInterval.get_bounds()
        if vmax<vmin:
            vmin, vmax = vmax, vmin
        vmin = self._base.ge(vmin)

        locs =  frange(vmin, vmax+0.001*self._base.get_base(), self._base.get_base())

        return locs

    def autoscale(self):
        """
        Set the view limits to the nearest multiples of base that
        contain the data
        """

        self.verify_intervals()
        dmin, dmax = self.dataInterval.get_bounds()

        vmin = self._base.le(dmin)
        vmax = self._base.ge(dmax)
        if vmin==vmax:
            vmin -=1
            vmax +=1

        return self.nonsingular(vmin, vmax)

def scale_range(vmin, vmax, n = 1, threshold=100):
    dv = abs(vmax - vmin)
    if dv == 0:
        return 1.0, 0.0
    meanv = 0.5*(vmax+vmin)
    if abs(meanv)/dv < threshold:
        offset = 0
    elif meanv > 0:
        ex = divmod(math.log10(meanv), 1)[0]
        offset = 10**ex
    else:
        ex = divmod(math.log10(-meanv), 1)[0]
        offset = -10**ex
    ex = divmod(math.log10(dv/n), 1)[0]
    scale = 10**ex
    return scale, offset



class MaxNLocator(Locator):
    """
    Select no more than N intervals at nice locations.
    """

    def __init__(self, nbins = 10, steps = None, trim = True):
        self._nbins = int(nbins)
        self._trim = trim
        if steps is None:
            self._steps = [1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10]
        else:
            if int(steps[-1]) != 10:
                steps = list(steps)
                steps.append(10)
            self._steps = steps

    def bin_boundaries(self, vmin, vmax):
        nbins = self._nbins
        scale, offset = scale_range(vmin, vmax, nbins)
        vmin -= offset
        vmax -= offset
        raw_step = (vmax-vmin)/nbins
        scaled_raw_step = raw_step/scale

        for step in self._steps:
            if step < scaled_raw_step:
                continue
            step *= scale
            best_vmin = step*divmod(vmin, step)[0]
            best_vmax = best_vmin + step*nbins
            if (best_vmax >= vmax):
                break
        if self._trim:
            extra_bins = int(divmod((best_vmax - vmax), step)[0])
            nbins -= extra_bins
        return (arange(nbins+1) * step + best_vmin + offset)


    def __call__(self):
        self.verify_intervals()
        vmin, vmax = self.viewInterval.get_bounds()
        vmin, vmax = self.nonsingular(vmin, vmax, expander = 0.05)
        return self.bin_boundaries(vmin, vmax)

    def autoscale(self):
        self.verify_intervals()
        dmin, dmax = self.dataInterval.get_bounds()
        dmin, dmax = self.nonsingular(dmin, dmax, expander = 0.05)
        return take(self.bin_boundaries(dmin, dmax), [0,-1])


def decade_down(x, base=10):
    'floor x to the nearest lower decade'

    lx = math.floor(math.log(x)/math.log(base))
    return base**lx

def decade_up(x, base=10):
    'ceil x to the nearest higher decade'
    lx = math.ceil(math.log(x)/math.log(base))
    return base**lx

def is_decade(x,base=10):
    lx = math.log(x)/math.log(base)
    return lx==int(lx)

class LogLocator(Locator):
    """
    Determine the tick locations for log axes
    """

    def __init__(self, base=10.0, subs=[1.0]):
        """
        place ticks on the location= base**i*subs[j]
        """
        self.base(base)
        self.subs(subs)

    def base(self,base):
        """
        set the base of the log scaling (major tick every base**i, i interger)
        """
        self._base=base+0.0

    def subs(self,subs):
        """
        set the minor ticks the log scaling every base**i*subs[j]
        """
        if subs is None:
            self._subs = None  # autosub
        else:
            self._subs = array(subs)+0.0



    def __call__(self):
        'Return the locations of the ticks'
        self.verify_intervals()
        b=self._base

        vmin, vmax = self.viewInterval.get_bounds()
        vmin = math.log(vmin)/math.log(b)
        vmax = math.log(vmax)/math.log(b)

        if vmax<vmin:
            vmin, vmax = vmax, vmin
        ticklocs = []

        numdec = math.floor(vmax)-math.ceil(vmin)
        if self._subs is None: # autosub
            if numdec>10: subs = array([1.0])
            elif numdec>6: subs = arange(2.0, b, 2.0)
            else: subs = arange(2.0, b)
        else:
            subs = self._subs
        for decadeStart in b**arange(math.floor(vmin),math.ceil(vmax)):
            ticklocs.extend( subs*decadeStart )

        if(len(subs) and subs[0]==1.0):
            ticklocs.append(b**math.ceil(vmax))


        ticklocs = array(ticklocs)
        ind = nonzero(logical_and(ticklocs>=b**vmin ,
                                  ticklocs<=b**vmax))


        ticklocs = take(ticklocs,ind)
        return ticklocs



    def autoscale(self):
        'Try to choose the view limits intelligently'
        self.verify_intervals()

        vmin, vmax = self.dataInterval.get_bounds()
        if vmax<vmin:
            vmin, vmax = vmax, vmin

        minpos = self.dataInterval.minpos()

        if minpos<=0:
            raise RuntimeError('No positive data to plot')
        if vmin<=0:
            vmin = minpos
        if not is_decade(vmin,self._base): vmin = decade_down(vmin,self._base)
        if not is_decade(vmax,self._base): vmax = decade_up(vmax,self._base)
        if vmin==vmax:
            vmin = decade_down(vmin,self._base)
            vmax = decade_up(vmax,self._base)
        return self.nonsingular(vmin, vmax)

class AutoLocator(MaxNLocator):
    def __init__(self):
        MaxNLocator.__init__(self, nbins=9, steps=[1, 2, 5, 10])

class OldAutoLocator(Locator):
    """
    On autoscale this class picks the best MultipleLocator to set the
    view limits and the tick locs.

    """
    def __init__(self):
        self._locator = LinearLocator()

    def __call__(self):
        'Return the locations of the ticks'
        self.refresh()
        return self._locator()

    def refresh(self):
        'refresh internal information based on current lim'
        d = self.viewInterval.span()
        self._locator = self.get_locator(d)

    def autoscale(self):
        'Try to choose the view limits intelligently'

        self.verify_intervals()
        d = abs(self.dataInterval.span())
        self._locator = self.get_locator(d)
        return self._locator.autoscale()

    def get_locator(self, d):
        'pick the best locator based on a distance'
        d = abs(d)
        if d<=0:
            locator = MultipleLocator(0.2)
        else:

            try: ld = math.log10(d)
            except OverflowError:
                raise RuntimeError('AutoLocator illegal dataInterval range')


            fld = math.floor(ld)
            base = 10**fld

            #if ld==fld:  base = 10**(fld-1)
            #else:        base = 10**fld

            if   d >= 5*base : ticksize = base
            elif d >= 2*base : ticksize = base/2.0
            else             : ticksize = base/5.0
            #print 'base, ticksize, d', base, ticksize, d, self.viewInterval

            #print self.dataInterval, d, ticksize
            locator = MultipleLocator(ticksize)

        locator.set_view_interval(self.viewInterval)
        locator.set_data_interval(self.dataInterval)
        return locator



__all__ = ('TickHelper', 'Formatter', 'FixedFormatter',
           'NullFormatter', 'FuncFormatter', 'FormatStrFormatter',
           'ScalarFormatter', 'LogFormatter', 'LogFormatterExponent',
           'LogFormatterMathtext', 'Locator', 'IndexLocator',
           'FixedLocator', 'NullLocator', 'LinearLocator',
           'LogLocator', 'AutoLocator', 'MultipleLocator',
           'MaxNLocator', )
