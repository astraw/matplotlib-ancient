matplotlib examples
===================

There are a variety of ways to use matplotlib, and most of them are
illustrated in the examples in this directory.

Probably the most common way people use matplotlib is with the
procedural interface, which follows the matlab/IDL/mathematica
approach of using simple procedures like "plot" or "title" to modify
the current figure.  These examples are included in the "pylab_examples"
directory.  If you want to write more robust scripts, eg for
production use or in a web application server, you will probably want
to use the matplotlib API for full control.  These examples are found
in the "api" directory.  Below is a brief description of the different
directories found here:

  * animation - dynamic plots, see the tutorial at
    http://www.scipy.org/Cookbook/Matplotlib/Animations

  * api - working with the matplotlib API directory.  See the
    doc/artist_api_tut.txt in the matplotlib src directory ((PDF at
    http://matplotlib.sf.net/pycon)

  * data - some data files we use in the examples

  * event_handling - how to interact with your figure, mouse presses,
    key presses, object picking, etc.  See the event handling tutorial
    in the "doc" directory of the source distribution (PDF at
    http://matplotlib.sf.net/pycon)

  * misc - some miscellaneous examples.  some demos for loading and
    working with record arrays

  * pylab_examples - the  interface to matplotlib similar to matlab

  * tests - tests used by matplotlib developers to check functionality

  * units - working with unit data an custom types in matplotlib

  * user_interfaces - using matplotlib in a GUI application, eg
    TkInter, WXPython, pygtk, pyqt or FLTK widgets

