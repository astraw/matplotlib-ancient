"""Fractal Dimension exercise"""

from IterateLogistic import *

def GetPn(mu, epsilonList, nSampleMax, nTransient=10000):
    """
    Generates probability arrays P_n[epsilon]. 
    Specifically,
     finds a point on the attractor by iterating nTransient times
     collects points on the attractor of size nSample
     for each epsilon in epsilonList, 
      generates bins of size epsilon for the range (0,1) of the function
          bins = scipy.arange(0.0,1.0+eps,eps)
      finds the number of points from the sample in each bin, using
      the histogram function
          numbers, bins = matplot.hist(sample, bins=bins, noplot=1)
      and computes the probability P_n[epsilon] of being in each bin.
    In the period doubling region the sample should of size 2^n so that 
    it covers the attractor evenly.
    """
    pass


def DimensionEstimates(mu, epsilonList, nSampleMax):
    """
    Estimates the capacity dimension and the information dimension 
    for a sample of points on the line.
    The capacity dimension is defined as
       D_capacity = lim {eps->0} (- log(Nboxes) / log(eps))
    but converges faster as
       D_capacity = - (log(Nboxes[i+1])-log(Nboxes[i])) 
       			/ (log(eps[i+1])-log(eps[i]))
    where Nboxes is the number of intervals of size eps needed to 
    cover the space. The information dimension is defined as
       D_inf = lim {eps->0} sum(P_n log P_n) / log(eps)
    but converges faster as
       S0 = sum(P_n log P_n)
       D_inf = - (S0[i+1]-S0[i]) 
       			/ (log(eps[i+1])-log(eps[i]))
    where P_n is the fraction of the list 'sample' that is in bin n,
    and the bins are of size epsilon. You'll need to add a small 
    increment delta to P_n before taking the log: delta = 1.e-100 will 
    not change any of the non-zero elements, and P_n log (P_n + delta)
    will be zero if P_n is zero.

    Returns three lists, with epsilonBar (geometric mean of neighboring
    epsilonList values), and D_inf, and D_capacity values for each 
    epsilonBar
    """
    pass


def PlotDimensionEstimates(mu, nSampleMax = 2**18, \
                           epsilonList=2.0**scipy.arange(-4,-16,-1)):
    """
    Plots capacity and information dimension estimates versus 
    epsilon, to allow one to visually extrapolate to zero. 
    Uses matplot.semilogx.

    We found using from 16 to one million bins useful. In the chaotic 
    region, the sample should be larger than the number of bins.

    Try mu = 0.9 in the chaotic region; compare with
    mu=0.9, nSampleMax = 10000 to see what the 'finite sample' effects of
    having fewer points than bins looks like.

    Try mu = 0.8 in the periodic limit cycle region. Are the dimensions
    of the attractor different?

    Try muInfinity = 0.892486418. Does the graph extrapolate to 
    near D_inf = 0.517098 and D_capacity = 0.538, as measured in the
    literature? 

    Try muInfinity +- 0.001, to see how the dimension of the attractor
    looks fractal on long length scales (big epsilon), but becomes 
    homogeneous on short length scales. This is the reverse of what 
    happens in percolation. It's because short length scales correspond 
    to long time scales...
    """
    pass


def demo():
    """Demonstrates solution for exercise: example of usage"""
    nSampleMax = 2**16
    epsilonList=2.0**scipy.arange(-4,-16,-1)
    muInfinity = 0.892486418
    print "Fractal Dimensions Demo"
    print "Close plots to continue"
    print "  Attractor becomes fractal at muInfinity = 0.892486..."
    BifurcationDiagram(f, 0.1, 500, 128, scipy.arange(0.89, 0.894, 0.00003))
    print "  Fractal Dimension Estimates at mu=0.9 (should be one)"
    PlotDimensionEstimates(0.9, nSampleMax = nSampleMax, \
                           epsilonList=epsilonList)
    print "  Fractal Dimension Estimates at mu=0.89 (should be zero)"
    PlotDimensionEstimates(0.89, nSampleMax = nSampleMax, \
                           epsilonList=epsilonList)
    print "  Fractal Dimension Estimates at mu=muInfinity (should be theory)"
    PlotDimensionEstimates(muInfinity, nSampleMax = nSampleMax, \
                           epsilonList=epsilonList)
