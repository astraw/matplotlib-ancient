"""Example script with an expensive initialization.

Meant to be used via ipython's %run -i, though it can run standalone."""

# Imagine that bigobject is actually something whose creation is an expensive
# process, though here we are just going to make it a list of numbers for
# demonstration's sake.  The trick is to trap a test for the existence of this
# name in a try/except block.  If the object exists, we don't recreate it, if
# it doesn't exist yet (such as the first time the code is run in any given
# session), we make it.

try:
    bigobject
    print "We found bigobject! No need to initialize it."
except NameError:
    print "bigobject not found, performing expensive initialization..."
    bigobject = range(1000)

# And now you can move on with working on bigobject:
total = sum(bigobject)
print 'total is:',total
