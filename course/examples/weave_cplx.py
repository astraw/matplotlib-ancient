#!/usr/bin/env python
###########################################################################
from Numeric import *
from weave import *

def complex_test():
    a = zeros((4,4),Complex)
    a[0,0] = 1+2j
    a[1,1] = 2+3.5j
    print 'Before\n',a
    code = \
"""
std::complex<double> i(0, 1);
std::cout << a(1,1) << std::endl;
a(2,2) = 3.0+4.5*i;
//a(2,2).imag = 4.5;
"""
    inline(code,['a'],type_converters = converters.blitz)
    print 'After\n',a

complex_test()
###########################################################################
