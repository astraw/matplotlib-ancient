"""Invariant Measure exercise"""

from IterateLogistic import *

def PlotInvariantDensityWithBoundaries(g, x0, num_boundaries, 
                                       args=(), xMax=0.5):
    """Plots the invariant density, together with the first num_boundaries
    iterates of xMax = 0.5 (which should coincide with folds, and hence
    cusps, in the invariant density). Plots the iterates f^[n](xMax) as red
    circles 'ro' at rho = n."""
    pass

def PlotBoundaries(g, nImages, etaArray, xMax=0.5):
    """
    For each parameter value eta in etaArray,
    iterate the point xMax nImages times, and plot the result
    (not including xMax) versus eta. We recommend using
       matplot.plot(etas, halfImages, 'ro')
    where the 'ro' will draw red circles.

    Usually xMax will be the peak in the function g (as hinted at by 
    its name).
    
    This can be used in conjunction with BifurcationDiagram to explain
    the boundary structure in the chaotic region. If you remove 
    matplot.show() from BifurcationDiagram, this plot will be 
    superimposed on the other.
    """
    pass

def demo():
    """Demonstrates solution for exercise: example of usage"""
    print "Invariant Measure Demo"
    print "Close plots to continue"
    print "  Creating Invariant Density at mu=0.9"
    PlotInvariantDensityWithBoundaries(f,0.1,20,(0.9,))
    print "  Creating Bifurcation Diagram With Boundaries"
    BifurcationDiagram(f, 0.1, 500, 128, scipy.arange(0.8, 1.00001, 0.002),
                           showPlot=False)
    PlotBoundaries(f, 6, scipy.arange(0.8, 1.00001, 0.002))

