from __future__ import division

def WallisPi(n,longform=0):
    """Compute pi using n terms of Wallis' product.
    
    If longform is true, the result is returned as a long integer of the
    form 314..."""
    
    num = 1L
    den = 1L
    for i in range(1,n+1):
	tmp = 4*i*i
	num *= tmp
	den *= tmp-1
    if longform == 0:
	return 2.0*(num/den)
    else:
	order = len(str(num))+1
	return long(10**order)*2*num//den
