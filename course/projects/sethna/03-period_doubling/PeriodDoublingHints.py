"""
Period Doubling exercise.
"""

from IterateLogistic import *

def fsin(x, B):
    """
    Sine map f_sin(x) = B sin(pi x), which also folds the unit interval
    (0,1) into itself."""
    pass


def PlotIterate(g, x0, N, args=()):
    """
    Plots g, the diagonal y=x, and the boxes made of the segments
    [[x0,x0], [x0, g(x0)], [g(x0), g(x0)], [g(x0), g(g(x0))], ...
    """
    pass


def FindSuperstable(g, nIterated, etaMin, etaMax, xMax=0.5):
    """
    Finds superstable orbit g^[nIterated](xMax, eta) = xMax
    in range (etaMin, etaMax). 
    Must be started with g-xMax of different sign at etaMin, etaMax.
   
    Uses scipy.optimize.brentq, defining a temporary function, fn(eta)
    which is zero for the superstable value of eta.

    fn iterates g nIterated times and subtracts xMax
    (basically Iterate - xMax, except with only one argument eta)
    """
    pass


def GetSuperstablePoints(g, nMax, eta0, eta1, xMax=0.5):
    """
    Given the parameters for the first two superstable parameters eta_ss[0] 
    and eta_ss[1], finds the next nMax-1 of them up to eta_ss[nMax].
    Returns dictionary eta_ss 

    Usage:
        Find the value of the parameter eta_ss[0] = eta0 for which the fixed
	point is xMax and g is superstable (g(xMax) = xMax), and the 
	value eta_ss[1] = eta1 for which g(g(xMax)) = xMax, either
	analytically or using FindSuperstable by hand.
        mus = GetSuperstablePoints(f, 9, eta0, eta1)

    Searches for eta_ss[n] in the range (etaMin, etaMax), 
    with etaMin = eta_ss[n-1] + epsilon and
    etaMax = eta_ss[n-1] + (eta_ss[n-1]-eta_ss[n-2])/A
    where A=3 works fine for the maps I've tried.
    (Asymptotically, A should be smaller than but comparable to delta.)
    """
    pass


def DeltaAlpha(g, eta_ss, xMax=0.5):
    """
    Given superstable 2^n cycle values eta_ss[n], calculates 
    delta[n] = (eta_{n-1}-eta_{n-2})/(eta_{n}-eta_{n-1}),
    sep[n] = distance from xMax to attractor point halfway around circle,
    and alpha = sep[n-1]/sep[n]

    Also extrapolates eta to etaInfinity using definition of delta and 
    most reliable value for delta:
    delta = lim{n->infinity} (eta_{n-1}-eta_{n-2})/(eta_n - eta_{n-1})

    Returns delta and alpha dictionaries for n>=2, and etaInfinity
    """
    pass


def FindScalingConvergence(g, nMax, xMax=0.5):
    """
    Finds eta0, eta1:
      Assumes superstable fixed point eta0 is between 0.3 and 1,
      superstable period two cycle eta1 is between eta0+epsilon and 1
    Calls GetSuperstablePoints
    Calls DeltaAlpha
    Returns etas, deltas, alphas, etaInfinity
    """
    pass


def PlotFIterated(g, n, args):
    """
    Plots g^[2^n](x,*args) versus x, along with the curve y=x.
    Also can plot box with corners (1-x*, 1-x*), (x*, x*) 
    """
    pass


def XStar(g, args=(), xMax = 0.5):
    """
    Finds fixed point of one-humped map g, which is assumed to be
    between xMax and 1.0.
    """
    pass


def Alpha(g, args=(), xMax = 0.5):
    """
    Finds the (negative) scale factor alpha which inverts and rescales
    the small inverted region of g(g(x)) running from (1-x*) to x*.
    """
    pass


class T:
    """
    Creates a new function T[g] from g, implementing Feigenbaum's
    renormalization-group transformation of function space into itself.

    We define it as a class so that we can initialize alpha and xStar,
    which otherwise would need to be recalculated each time T[g] was
    evaluated at a point x.

    Usage:
        Tg = T(g, args)
        Tg(x) evaluates the function at x
    """
    def __init__(self, g, args=(), xMax=0.5):
        """
	Stores g and args. 
	Calculates and stores xStar and alpha.
	"""
	pass
    def __call__(self, x):
        """
        Defines xShrunk to be x/alpha + x*
	Evaluates g2 = g(g(xShrunk))
	Returns expanded alpha*(g2-xStar)
	"""
	pass


def PlotTgVsG(g, args, xMax=0.5):
    """Plots Tg(x) and g(x) on the same plot, for x from (0,1)"""
    pass


def PlotTIterates(g, args, nMax = 2, xMax=0.5):
    """
    Plots g(x), T[g](x), T[T[g]](x) ... 
    on the same plot, for x from (0,1)
    """
    pass


def PlotT2FVsT2Fsin():
    """
    Plots T[T[f]](x), T[T[fsin]](x) ... 
    on the same plot, for x from (0,1)
    """
    pass

def demo():
    """Demonstrates solution for exercise: example of usage"""
    print "Period Doubling Demo"
    print "Close plots to continue"
    mus, deltas, alphas, muInfinity = FindScalingConvergence(f,9)
    print "  Fixed Point, mu=0.7"
    print "  (Close plot to continue)"
    PlotIterate(f,0.1,20,(0.7,))
    print "  Period Doubling: mu=0.8"
    PlotIterate(f,0.1,100,(0.8,))
    print "  Chaos: mu=0.9"
    x0 = Iterate(f,0.5,100,(0.9,))
    PlotIterate(f,x0,100,(0.9,))
    print "  Onset of Chaos: mu=muInfinity"
    x0 = Iterate(f,0.5,100,(muInfinity,))
    PlotIterate(f,x0,100,(muInfinity,))
    print "  Scaling in Bifurcation Diagram"
    # Optional 
    FastBifurcationDiagramWithBoxes(0.1,2000,128,scipy.arange(0.4,1.0,0.002),
    				    mus,muInfinity)
    print "  Convergence of alpha, delta, mu to scaling values"
    matplot.plot(mus.keys(), mus.values(), "ro", label="mu")
    matplot.plot(deltas.keys(), deltas.values(), "go", label = "delta")
    matplot.plot(alphas.keys(), alphas.values(), "bo", label = "alpha")
    matplot.legend()
    matplot.show()
    print "  Renormalization-group Transformation"
    PlotFIterated(f, 1, (muInfinity,))
    print "  Renormalization-group Transformation Twice"
    # Optional
    PlotFIteratedAllBoxes(f, 2, (muInfinity,), alphas[9])
    print "  Repeated renormalization-group transformations"
    PlotTIterates(f, (muInfinity,))
    print "  Universality: T^2 of sine map and logistic map agree"
    print "  (Zoom in to see difference)"
    PlotT2FVsT2Fsin()
