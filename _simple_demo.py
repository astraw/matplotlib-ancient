"""
Provides simple demos to be called from the development code

"""

from matplotlib.figure import Figure, Subplot
import Numeric as numpy

def subplot_demo():
    f = Figure()
    t = numpy.arange(0.0,3.0,0.01)
    s1 = numpy.sin(2*numpy.pi*t)
    s2 = numpy.zeros(t.shape, numpy.Float)

    a1 = Subplot(211)
    a1.plot(t,s1)
    a1.set_title('And now for something completely different')

    a2 = Subplot(212)
    a2.plot(t,s2)
    a2.set_xlabel('time (s)')

    f.add_axis(a1)
    f.add_axis(a2)
    f.show()
