#!/usr/bin/env python
"""Sieve of Erathostenes"""

import sys
import math

def sieve_quad(nmax):
    """Return an array of prime numbers up to nmax, using Erathostenes' sieve.

    Naive, O(N^2) implementation."""

    first = 3
    primes_head = []
    primes_tail = N.arange(first,nmax+1,2)
    while first <= int(round(N.sqrt(primes_tail[-1]))):
	first = primes_tail[0]
	primes_head.append(first)
	non_primes = first * primes_tail
	primes_tail = N.array([ n for n in primes_tail[1:] if not n in non_primes ])
    return N.concatenate((primes_head,primes_tail))

def sieve(nmax):
    """Return a list of prime numbers up to nmax, using Erathostenes' sieve.

    This is a far more efficient implementation than sieve_quad: we combine a
    dictionary with an auxiliary list (kept sorted).

    The timing behavior of this version shows some interesting jumps, which
    don't appear in sieve2().  sieve2() seems to have much smoother behavior,
    averaging the same as this one asymptotically.

    These jumps are caused by python's builtin list sort() method: for some
    values it's a lot better than Numeric's sort() function, for others it's a
    LOT worse.  Using Numeric.sort() here basically makes this version and
    sieve2() behave identically.  I'll need to check with python 2.3 (where
    supposedly sort was much improved) for differences."""

    #import Numeric as N

    # Sanity checks
    assert nmax>0, \
	   "nmax must be a non-negative number"
    if nmax == 1:
	return [1]
    elif nmax == 2:
	return [1,2]
    
    # Initialization
    primes_head = [1,2]
    # The primes tail will be kept both as a dict and as a sorted list
    primes_tail = {}
    primes_tail_lst = range(3,nmax+1,2)
    for p in primes_tail_lst:
	primes_tail[p] = 1
	
    # Now do the actual sieve
    first = primes_tail_lst[0]
    while first <= round(math.sqrt(primes_tail_lst[-1])):
	# Move the first leftover prime from the dict to the head list
	first = primes_tail_lst[0]
	del primes_tail[first]  # remove it from the dict
	primes_head.append(first) # and store it in the head list

	# Now, remove from the primes tail all non-primes.  For us to be able
	# to break as soon as a key is not found, it's crucial that the tail
	# list is always sorted.

	for next_candidate in primes_tail_lst:
	    # Note: the try/except approach seems a bit faster than
	    # checking with has_key().
	    try:
		del primes_tail[first*next_candidate]
	    except KeyError:
		break
	# Build a new sorted tail list with the leftover keys
	primes_tail_lst = primes_tail.keys()
	primes_tail_lst.sort()
	#primes_tail_lst = N.sort(primes_tail.keys())

    # dbg
    hsize = len(primes_head)
    tsize = len(primes_tail_lst)
    tot = hsize+tsize
    print 'nmax,head,tail,total sizes:',nmax,hsize,tsize,tot
    # dbg
    return primes_head + primes_tail_lst

def sieve2(nmax):
    """Return an array of prime numbers up to nmax, using Erathostenes' sieve.

    This is a far more efficient implementation than sieve_quad: we combine a
    dictionary with an auxiliary list (kept sorted).

    This version uses Numeric, so it's limited to the range of C integers."""

    import Numeric as N
    # Sanity checks
    assert isinstance(nmax,int) and nmax>0, \
	   "nmax must be a non-negative integer"
    if nmax == 1:
	return N.array([1])
    elif nmax == 2:
	return N.array([1,2])
    # Initialization
    primes_head = [1,2]
    # The primes tail will be kept both as a dict and as a sorted array
    primes_tail = {}
    primes_tail_arr = N.arange(3,nmax+1,2)
    for p in primes_tail_arr:
	primes_tail[p] = 1

    # Now do the actual sieve
    first = primes_tail_arr[0]
    while first <= round(math.sqrt(primes_tail_arr[-1])):
	# Move the first leftover prime from the dict to the head list
	first = primes_tail_arr[0]
	del primes_tail[first]  # remove it from the dict
	primes_head.append(first) # and store it in the head list

	# Now, compute the array of non-primes And remove from the primes tail
	# all non-primes.  For us to be able to break as soon as a key is not
	# found, it's crucial that the tail array is always sorted.

	for non_prime in first*primes_tail_arr:
	    try:
		del primes_tail[non_prime]
	    except KeyError:
		break
	# Build a new sorted tail array with the leftover keys
	primes_tail_arr = N.sort(primes_tail.keys())
    return N.concatenate((primes_head,primes_tail_arr))

def time_rng(fun,nrange,ret_both=0,verbose=1):
    """Time a function over a range of parameters, return the list of times.

    The function should be callable with a single argument: it will be called
    with each entry from nrange in turn.

    If verbose is true, at each step the value of nrange and time for the call
    is printed."""

    from IPython.genutils import timing
    
    time_n = lambda n: timing(fun,n)
    times = []
    write = sys.stdout.write
    flush = sys.stdout.flush
    for n in nrange:
	t = time_n(n)
	if verbose:
	    if verbose==1:
		write('.')
	    elif verbose>1:
		print n,t
	    flush()
	times.append(t)

    if ret_both:
	return nrange,times
    else:
	return times
