#!/usr/bin/env python
"""Simple examples of weave use.

Code meant to be used for learning/testing, not production.

Fernando Perez <fperez@colorado.edu>
March 2002, updated 2003."""

from weave import inline,converters
from Numeric import *

#-----------------------------------------------------------------------------
def simple_print(input):
    """Simple print test.

    Since there's a hard-coded printf %i in here, it will only work for numerical
    inputs (ints).  """

    # note in the printf that newlines must be passed as \\n:
    code = '''
    std::cout << "Printing from C++ (using std::cout) : "<<input<<std::endl;
    printf("And using C syntax (printf)    : %i\\n",input);
    '''
    inline(code,['input'],
           verbose=2)  # see inline docstring for details

def py_print(input):
    "Trivial printer, for timing."
    print "Input:",input

def c_print(input):
    "Trivial printer, for timing."
    code = """printf("Input: %i \\n",input);"""
    inline(code,['input'])

def cpp_print(input):
    "Trivial printer, for timing."
    code = """std::cout << "Input: " << input << std::endl;"""
    inline(code,['input'])
 
#-----------------------------------------------------------------------------
# Returning a scalar quantity computed from a Numeric array.
def trace(mat):
    """Return the trace of a matrix.
    """
    nrow,ncol = mat.shape
    code = \
""" 
double tr=0.0;

for(int i=0;i<nrow;++i)
    tr += mat(i,i);
return_val = tr;
"""
    return inline(code,['mat','nrow','ncol'],
                  type_converters = converters.blitz)

#-----------------------------------------------------------------------------
# WRONG CODE: trace() version which modifies in-place a python scalar
# variable.  Note that this doesn't work, similarly to how in-place changes in
# python only work for mutable objects. Below is an example that does work.
def trace2(mat):
    """Return the trace of a matrix. WRONG CODE.
    """
    nrow,ncol = mat.shape
    tr = 0.0
    code = \
""" 
for(int i=0;i<nrow;++i)
    tr += mat(i,i);
"""
    inline(code,['mat','nrow','ncol','tr'],
           type_converters = converters.blitz)
    return tr

#-----------------------------------------------------------------------------
# Operating in-place in an existing Numeric array. Contrary to trying to modify
# in-place a scalar, this works correctly.
def in_place_mult(num,mat):
    """In-place multiplication of a matrix by a scalar.
    """
    nrow,ncol = mat.shape
    code = \
"""
for(int i=0;i<nrow;++i)
    for(int j=0;j<ncol;++j)
	mat(i,j) *= num;

"""
    inline(code,['num','mat','nrow','ncol'],
           type_converters = converters.blitz)

#-----------------------------------------------------------------------------
# Pure Python version for checking.
def cross_product(a,b):
    """Cross product of two 3-d vectors.
    """
    cross = [0]*3
    cross[0] = a[1]*b[2]-a[2]*b[1]
    cross[1] = a[2]*b[0]-a[0]*b[2]
    cross[2] = a[0]*b[1]-a[1]*b[0]
    return array(cross)

#-----------------------------------------------------------------------------
# Here we return a list from the C code. This is probably *much* slower than
# the python version, it's meant as an illustration and not as production
# code.
def cross_productC(a,b):
    """Cross product of two 3-d vectors.
    """
    # py::tuple or py::list both work equally well in this case.
    code = \
"""
py::tuple cross(3);

cross[0] = a(1)*b(2)-a(2)*b(1);
cross[1] = a(2)*b(0)-a(0)*b(2);
cross[2] = a(0)*b(1)-a(1)*b(0);
return_val = cross;
"""
    return array(inline(code,['a','b'],
                        type_converters = converters.blitz))

#-----------------------------------------------------------------------------
# C version which accesses a pre-allocated NumPy vector.  Note: when using
# blitz, index access is done with (,,), not [][][]. In fact, [] indexing
# fails silently. See this and the next version for a comparison.
def cross_productC2(a,b):
    """Cross product of two 3-d vectors.
    """

    cross = zeros(3,a.typecode())
    code = \
"""
cross(0) = a(1)*b(2)-a(2)*b(1);
cross(1) = a(2)*b(0)-a(0)*b(2);
cross(2) = a(0)*b(1)-a(1)*b(0);
"""
    inline(code,['a','b','cross'],
           type_converters = converters.blitz)
    return cross

#-----------------------------------------------------------------------------
# Just like the previous case, but now we don't use the blitz converters.
# Weave automagically does the type conversions for us.
def cross_productC3(a,b):
    """Cross product of two 3-d vectors.
    """

    cross = zeros(3,a.typecode())
    code = \
""" 
cross[0] = a[1]*b[2]-a[2]*b[1];
cross[1] = a[2]*b[0]-a[0]*b[2];
cross[2] = a[0]*b[1]-a[1]*b[0];
"""
    inline(code,['a','b','cross'])

    return cross
    
#-----------------------------------------------------------------------------
def dot_product(a,b):
    """Dot product of two vectors.

    Implemented in a funny (ridiculous) way to use support_code.

    I want to see if we can call another function from inside our own
    code. This would give us a crude way to implement better modularity by
    having global constants which include the raw code for whatever C
    functions we need to call in various places. These can then be included
    via support_code.

    The overhead is that the support code gets compiled in *every* dynamically
    generated module, but I'm not sure that's a big deal since the big
    compilation overhead seems to come from all the fancy C++ templating and
    whatnot.

    Later: ask Eric if there's a cleaner way to do this."""
    
    N = len(a)
    support = \
"""
double mult(double x,double y) {
    return x*y;
}
"""
    code = \
"""
double sum = 0.0;
for (int i=0;i<N;++i) {
    sum += mult(a(i),b(i));
}
return_val = sum;
"""
    return inline(code,['a','b','N'],
                  type_converters = converters.blitz,
                  support_code = support,
                  libraries = ['m'],
                  )

#-----------------------------------------------------------------------------
def sumC(x):
    """Return the sum of the elements of a 1-d array.
    
    An example of how weave accesses a Numeric array without blitz.  """

    num_types = {Float:'double',
                 Float32:'float'}
    x_type = num_types[x.typecode()]
    
    code = """
           double result=0.0;
           double element;

           for (int i = 0; i < Nx[0]; i++){

               // Note the type of the pointer below is computed in python
               //element = *(%s *)(x->data+i*x->strides[0]);

               // Weave's magic does the above for us:
               element = x[i];
               
               result += element;
               std::cout << "Element " << i << " = " << element << "\\n";
           }
           std::cout << "size x " << Nx[0] << "\\n";

           return_val = result;
           """ % x_type;

    return inline(code,['x'],verbose=0)

#-----------------------------------------------------------------------------
def Cglobals(arr):
    """How to pass data from function to function via globals.

    This allows the kind of 'over the head' parameter passing via globals
    which is ugly but necessary for using things like generic integrators in
    Numerical Recipes with aditional parameters.  """

    support = \
"""
// Declare globals here

/* These blitz guys must be accessed via pointers to avoid a costly copy.
Note that now the type is hardwired in. All python polymorphism is gone.  I
should look into whether this can be fixed by properly using blitz templating.
*/
blitz::Array<int, 1> *G_arr_pt;

// The global M will be visible in the "code" segment
int M = 99;

void aprint(int N) {
  std::cout << "In aprint()\\n";
  for (int i=0;i<N;++i)
    std::cout << "arr[" << i << "]=" << (*G_arr_pt)(i) << " ";
  std::cout << std::endl;
}

"""
    code = \
"""
// Get the passed array reference so the data becomes global
G_arr_pt = &arr;

std::cout << "global M=" << M << std::endl;
std::cout << "local N=" << N << std::endl;


std::cout << "First, print using the blitz internal printer:\\n";
std::cout << "all arr\\n";
std::cout << arr << std::endl;

std::cout << "all G_arr\\n";
std::cout << *G_arr_pt << std::endl;

std::cout << "now by loop\\n";

for (int i=0;i<N;++i)
  std::cout << "arr[" << i << "]=" << arr(i) << " ";
std::cout << std::endl;


std::cout << "Now calling aprint\\n";

aprint(N);
"""
    N = len(arr)
    return inline(code,['arr','N'],
                  type_converters = converters.blitz,
                  support_code = support,
                  libraries = ['m'],
                  verbose = 0,
                  )


#-----------------------------------------------------------------------------
# Two trivial examples using the C math library follow.
def powC(x,n):
    """powC(x,n) -> x**n. Implemented using the C pow() function.
    """
    support = \
"""
#include <math.h>
"""
    code = \
"""
return_val = pow(x,n);
"""
    return inline(code,['x','n'],
                  type_converters = converters.blitz,
                  support_code = support,
                  libraries = ['m'],
                  )

# Some callback examples
def foo(x,y):
     print "In Python's foo:"
     print 'x',x
     print 'y',y
     return x

def cfoo(x,y):
      code = """
      printf("Attemtping to call back foo() from C...\\n");
      py::tuple foo_args(2);
      py::object z;  // This will hold the return value of foo()
      foo_args[0] = x;
      foo_args[1] = y;
      z = foo.call(foo_args);
      printf("Exiting C code.\\n");
      return_val = z;
      """
      return inline(code,"foo x y".split() )

x=99
y="Hello"

print "Pure python..."
z=foo(x,y)
print "foo returned:",z
print "\nVia weave..."
z=cfoo(x,y)
print "cfoo returned:",z

# Complex numbers
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

#-----------------------------------------------------------------------------
def sinC(x):
    """sinC(x) -> sin(x). Implemented using the C sin() function.
    """
    support = \
"""
#include <math.h>
"""
    code = \
"""
return_val = sin(x);
"""
    return inline(code,['x'],
                  type_converters = converters.blitz,
                  support_code = support,
                  libraries = ['m'],
                  )

def in_place_multNum(num,mat):
    mat *= num


from weave import inline
class bunch: pass

def oaccess():
    x=bunch()

    x.a = 1
    
    code = """ // BROKEN!
    // Try to emulate Python's: print 'x.a',x.a
    std::cout << "x.a " << x.a << std::endl;
    """
    inline(code,['x'])
    
main2 = oaccess


def ttest():
    nrun = 10
    size = 6000
    mat = ones((size,size),'d')
    num = 5.6
    tNum = time_test(nrun,in_place_multNum,*(num,mat))
    print 'time Num',tNum
    tC = time_test(nrun,in_place_mult,*(num,mat))
    print 'time C',tC

def main():
    print 'Printing comparisons:'
    print '\nPassing an int - what the C was coded for:'
    simple_print(42)
    print '\nNow passing a float. C++ is fine (cout<< takes care of things) but C fails:'
    simple_print(42.1)
    print '\nAnd a string. Again, C++ is ok and C fails:'
    simple_print('Hello World!')

    A = zeros((3,3),'d')

    A[0,0],A[1,1],A[2,2] = 1,2.5,3.3

    print '\nMatrix A:\n',A
    print 'Trace by two methods. Second fails, see code for details.'
    print '\ntr(A)=',trace(A)
    print '\ntr(A)=',trace2(A)

    a = 5.6
    print '\nMultiplying A in place by %s:' % a
    in_place_mult(a,A)
    print A

    # now some simple operations with 3-vectors.
    a = array([4.3,1.5,5.6])
    b = array([0.8,2.9,3.8])

    print '\nPython and C versions follow. Results should be identical:'
    print 'a =',a
    print 'b =',b

    print '\nsum(a_i) =',sum(a)
    print 'sum(a_i) =',sumC(a)

    print '\na.b =',dot(a,b)
    print 'a.b =',dot_product(a,b)

    print '\na x b =',cross_product(a,b)
    print 'a x b =',cross_productC(a,b)

    print '\nIn-place versions.'
    print 'a x b =',cross_productC2(a,b)
    print 'a x b =',cross_productC3(a,b)

    print '\nSimple functions using the C math library:'
    import math
    x = 3.5
    n = 4
    theta = math.pi/4.
    print '\nx**'+str(n)+'=',x**n
    print 'x**'+str(n)+'=',powC(x,n)
    print '\nsin('+str(theta)+')=',math.sin(theta)
    print 'sin('+str(theta)+')=',sinC(theta)

    print '\nGlobal variables and explicitly typed blitz arrays.'
    x = array([4,5,6])
    print 'x is a Numeric array:\nx=',x
    print 'Now using weave:'
    Cglobals (x)

if __name__ == '__main__':
    main()
