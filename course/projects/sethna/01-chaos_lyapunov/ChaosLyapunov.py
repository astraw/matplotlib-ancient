"""Invariant Measure exercise"""

from IterateLogistic import *

# Calculate Lyapunov exponent for mu=0.9
#
# traj = TrajectoryDifference(f,0.1,0.1000000000001, 100,(0.9,))
# p = FitLyapunovExponent(traj)
# p = p[0] # Weird error message removal
# PlotFit(traj, p)

def TrajectoryDifference(g, x1, x2, N, args=()):
    """
    Calculates the difference between two trajectories that start
    at two points x1 and x2, presumably close to one another.
    Returns list of length N+1,
    [x2-x1, g(x2)-g(x1), g(g(x2))-g(g(x1)), ...]

    Used for illustrating sensitive dependence on initial conditions for
    chaotic regions, and for calculating Lyapunov exponents.

    You can usefully pick x2-x1 comparable to machine precision (seventeen
    digits). Don't choose x1 or x2 to equal zero or one in the logistic 
    map: zero is an unstable fixed point.
    """

    xs1 = scipy.array(IterateList(g, x1, N, args))
    xs2 = scipy.array(IterateList(g, x2, N, args))
    return xs2-xs1


def PlotTrajectoryDifference(g, x1, x2, N, args=()):
    """
    Calls TrajectoryDifference to find the difference, then plots the 
    absolute value of the difference using 
        matplot.semilogy(scipy.fabs(dx)).
    (Given just one array, matplot assumes the other axis is just the
    index into the array.)

    Notice that the differences stop growing when they become of order 
    one (naturally). Don't use such long trajectories to calculate the 
    Lyapunov exponents: it will bias the results downward.
    """
    dx = TrajectoryDifference(g, x1, x2, N, args)
    matplot.semilogy(scipy.fabs(dx))
    matplot.show()


def LyapunovFitFunc(p, traj_diff):
    """
    Given a trajectory difference traj_diff and a tuple
        p = (lyapExponent, lyapLogPrefactor)
    returns the residuals 
        log(|y_n|) - log( exp(lyapLogPrefactor + lyapExponent * n) )

    The residual is the difference between the data and the fit:
    if the residuals were zero, the trajectory difference would be 
    perfectly described as a growing exponential.
    That is, the growth of the difference between two trajectories is 
    expected to be of the form
        |x_n - y_n| \sim lyapPrefactor * exp(lyapExponent n)

    We take the log of the difference so that the least--squares fit
    will emphasize the initial points and final points roughly equally.
    We use the log of the lyapPrefactor because it must be positive:
    it's a standard trick in nonlinear fitting to change variables like
    this to enforce ranges in parameters.

    Used by FitLyapunovExponent to generate a least-squares fit for 
    the Lyapunov exponent and prefactor.
    """
    lyapExponent, lyapLogPrefactor = p
    residuals = \
              scipy.log(scipy.fabs(traj_diff)) - \
              (lyapLogPrefactor + lyapExponent*scipy.arange(len(traj_diff)))
    return residuals


def FitLyapunovExponent(traj_diff, p0=(1., -13.)):
    """
    Given a trajectory difference and an initial guess 
    p0=(lyapExponent, lyapPrefactor) for the Lyapunov exponent and 
    prefactor, uses scipy.optimize.leastsq to do a best fit for 
    these two constants, and returns them.

    The return value will likely include a warning message, even though
    the fit seems fine and the warning meaningless. You'll likely need 
    to delete it before using PlotFit.
    """
    plsq = scipy.optimize.leastsq(LyapunovFitFunc, p0, args=(traj_diff,))
    return plsq # Lyapunov exponent and prefactor


def PlotFit(traj_diff, p):
    """
    Given a trajectory difference and p=(lyapExponent, lyapPrefactor),
    plot |traj_diff| and the fit on a semilog y axis.
    """
    
    matplot.plot(scipy.fabs(traj_diff), 'b-', linewidth=4)
    fit = scipy.exp(p[1] + p[0] * scipy.arange(len(traj_diff)))
    matplot.plot(fit, 'r-', linewidth=2)
    matplot.semilogy()
    matplot.show()

def demo():
    """Demonstrates solution for exercise: example of usage"""
    print "Chaos and Lyapunov Demo"
    print "  Creating trajectory difference and fit"
    print "  (Close plot to continue)"
    traj = TrajectoryDifference(f,0.1,0.1000000000001, 100,(0.9,))
    p = FitLyapunovExponent(traj)
    p = p[0] # Weird error message removal
    PlotFit(traj, p)

if __name__=="__main__":
    demo()
