#!/usr/bin/env python
from weave import inline

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
