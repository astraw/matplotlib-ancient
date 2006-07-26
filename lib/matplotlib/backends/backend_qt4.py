from __future__ import division
import math
import os
import sys

import matplotlib
from matplotlib import verbose
from matplotlib.numerix import asarray, fromstring, UInt8, zeros, \
     where, transpose, nonzero, indices, ones, nx
import matplotlib.numerix as numerix
from matplotlib.cbook import is_string_like, enumerate, onetrue
from matplotlib.font_manager import fontManager
from matplotlib.backend_bases import RendererBase, GraphicsContextBase, \
     FigureManagerBase, FigureCanvasBase, NavigationToolbar2, cursors
from matplotlib._pylab_helpers import Gcf
from matplotlib.figure import Figure
from matplotlib.mathtext import math_parse_s_ft2font
from PyQt4 import QtCore, QtGui

backend_version = "0.9.1"
def fn_name(): return sys._getframe(1).f_code.co_name

DEBUG = False

cursord = {
    cursors.MOVE          : QtCore.Qt.PointingHandCursor,
    cursors.HAND          : QtCore.Qt.WaitCursor,
    cursors.POINTER       : QtCore.Qt.ArrowCursor,
    cursors.SELECT_REGION : QtCore.Qt.CrossCursor,
    }

def draw_if_interactive():
    """
    Is called after every pylab drawing command
    """
    if matplotlib.is_interactive():
        figManager =  Gcf.get_active()
        if figManager != None:
            figManager.canvas.draw()

def show( mainloop=True ):
    """
    Show all the figures and enter the qt main loop
    This should be the last line of your script
    """
    for manager in Gcf.get_all_fig_managers():
        manager.window.show()
        
    if DEBUG: print 'Inside show'
    figManager =  Gcf.get_active()
    if figManager != None:
        figManager.canvas.draw()
        #if ( createQApp ):
        #   qtapplication.setMainWidget( figManager.canvas )

    if mainloop and createQApp:
        QtCore.QObject.connect( qtapplication, QtCore.SIGNAL( "lastWindowClosed()" ),
                            qtapplication, QtCore.SLOT( "quit()" ) )
        qtapplication.exec_()    


def new_figure_manager( num, *args, **kwargs ):
    """
    Create a new figure manager instance
    """
    thisFig = Figure( *args, **kwargs )
    canvas = FigureCanvasQT( thisFig )
    manager = FigureManagerQT( canvas, num )
    return manager


class FigureCanvasQT( QtGui.QWidget, FigureCanvasBase ):
    keyvald = { QtCore.Qt.Key_Control : 'control',
                QtCore.Qt.Key_Shift : 'shift',
                QtCore.Qt.Key_Alt : 'alt',
               }
    # left 1, middle 2, right 3
    buttond = {1:1, 2:3, 4:2}
    def __init__( self, figure ):
        if DEBUG: print 'FigureCanvasQt: ', figure
        FigureCanvasBase.__init__( self, figure )
        QtGui.QWidget.__init__( self )
        self.figure = figure
        self.setMouseTracking( True )

        w,h = self.get_width_height()
        self.resize( w, h )
        
    def mousePressEvent( self, event ):
        x = event.pos().x()
        # flipy so y=0 is bottom of canvas
        y = self.figure.bbox.height() - event.pos().y()
        button = self.buttond[event.button()]
        FigureCanvasBase.button_press_event( self, x, y, button )
        if DEBUG: print 'button pressed:', event.button()
        
    def mouseMoveEvent( self, event ):
        x = event.x()
        # flipy so y=0 is bottom of canvas
        y = self.figure.bbox.height() - event.y()
        FigureCanvasBase.motion_notify_event( self, x, y )
        if DEBUG: print 'mouse move'

    def mouseReleaseEvent( self, event ):
        x = event.x()
        # flipy so y=0 is bottom of canvas
        y = self.figure.bbox.height() - event.y()
        button = self.buttond[event.button()]
        FigureCanvasBase.button_release_event( self, x, y, button )
        if DEBUG: print 'button released'
        self.draw()

    def keyPressEvent( self, event ):
        key = self._get_key( event )
        FigureCanvasBase.key_press_event( self, key )
        if DEBUG: print 'key press', key

    def keyReleaseEvent( self, event ):
        key = self._get_key(event)
        FigureCanvasBase.key_release_event( self, key )
        if DEBUG: print 'key release', key

    def resizeEvent( self, event ):
        if DEBUG: print 'resize (%d x %d)' % (event.size().width(), event.size().height())
        QtGui.QWidget.resizeEvent( self, event )

    def resize( self, w, h ):
        QtGui.QWidget.resize( self, w, h )

    def _get_key( self, event ):
        if event.key() < 256:
            key = event.text().latin1()
        elif self.keyvald.has_key( event.key() ):
            key = self.keyvald[ event.key() ]
        else:
            key = None
            
        return key

class FigureManagerQT( FigureManagerBase ):
    """
    Public attributes

    canvas      : The FigureCanvas instance
    num         : The Figure number
    toolbar     : The qt.QToolBar
    window      : The qt.QMainWindow 
    """
    
    def __init__( self, canvas, num ):
        if DEBUG: print 'FigureManagerQT.%s' % fn_name()
        FigureManagerBase.__init__( self, canvas, num )
        self.canvas = canvas
        self.window = QtGui.QMainWindow()
        self.window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.window.setWindowTitle("Figure %d" % num)
        image = os.path.join( matplotlib.rcParams['datapath'],'matplotlib.png' )
        self.window.setWindowIcon(QtGui.QIcon( image ))

        centralWidget = QtGui.QWidget( self.window )
        self.canvas.setParent( centralWidget )
        
        # Give the keyboard focus to the figure instead of the manager
        self.canvas.setFocusPolicy( QtCore.Qt.ClickFocus )
        self.canvas.setFocus()

        QtCore.QObject.connect( self.window, QtCore.SIGNAL( 'destroyed()' ),
                            self._widgetclosed )
        self.window._destroying = False

        if matplotlib.rcParams['toolbar'] == 'classic':
            print "Classic toolbar is not yet supported"
            #self.toolbar = NavigationToolbarQT( centralWidget, canvas )
            self.toolbar = None
        elif matplotlib.rcParams['toolbar'] == 'toolbar2':
            self.toolbar = NavigationToolbar2QT( centralWidget, canvas )
        else:
            self.toolbar = None

        # Use a vertical layout for the plot and the toolbar.  Set the
        # stretch to all be in the plot so the toolbar doesn't resize.
        layout = QtGui.QVBoxLayout( centralWidget )
        layout.setMargin( 0 )
        layout.addWidget( self.canvas, 1 )
        if self.toolbar:
           layout.addWidget( self.toolbar, 0 )

        self.window.setCentralWidget( centralWidget )

        # Reset the window height so the canvas will be the right
        # size.  This ALMOST works right.  The first issue is that the
        # height w/ a toolbar seems to be off by just a little bit (so
        # we add 4 pixels).  The second is that the total width/height
        # is slightly smaller that we actually want.  It seems like
        # the border of the window is being included in the size but
        # AFAIK there is no way to get that size.  
        w = self.canvas.width()
        h = self.canvas.height()
        if self.toolbar:
           h += self.toolbar.height() + 4
        self.window.resize( w, h )
        
        if matplotlib.is_interactive():
            self.window.show()

        def notify_axes_change( fig ):
           # This will be called whenever the current axes is changed
           if self.toolbar != None: self.toolbar.update()
           self.canvas.figure.add_axobserver( notify_axes_change )

    def _widgetclosed( self ):
        if self.window._destroying: return
        self.window._destroying = True
        Gcf.destroy(self.num)

    def destroy( self, *args ):
        if self.window._destroying: return
        self.window._destroying = True
        if DEBUG: print "destroy figure manager"
        self.window.close(True)

class NavigationToolbar2QT( NavigationToolbar2, QtGui.QWidget ):
    # list of toolitems to add to the toolbar, format is:
    # text, tooltip_text, image_file, callback(str)
    toolitems = (
        ('Home', 'Reset original view', 'home.ppm', 'home'),
        ('Back', 'Back to  previous view','back.ppm', 'back'),
        ('Forward', 'Forward to next view','forward.ppm', 'forward'),
        (None, None, None, None),        
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move.ppm', 'pan'),
        ('Zoom', 'Zoom to rectangle','zoom_to_rect.ppm', 'zoom'),
        (None, None, None, None),
        ('Save', 'Save the figure','filesave.ppm', 'save_figure'),
        )
        
    def __init__( self, parent, canvas ):
        self.canvas = canvas
        QtGui.QWidget.__init__( self, parent )

        # Layout toolbar buttons horizontally.
        self.layout = QtGui.QHBoxLayout( self )
        self.layout.setMargin( 2 )
        self.layout.setSpacing( 0 )
        
        NavigationToolbar2.__init__( self, canvas )
        
    def _init_toolbar( self ):
        basedir = matplotlib.rcParams[ 'datapath' ]
        
        for text, tooltip_text, image_file, callback in self.toolitems:
            if text == None:
                self.layout.addSpacing( 8 )
                continue
            
            fname = os.path.join( basedir, image_file )
            image = QtGui.QPixmap()
            image.load( fname )

            button = QtGui.QPushButton( QtGui.QIcon( image ), "", self )
            button.setToolTip(tooltip_text)

            # The automatic layout doesn't look that good - it's too close
            # to the images so add a margin around it.
            margin = 4
            button.setFixedSize( image.width()+margin, image.height()+margin )

            QtCore.QObject.connect( button, QtCore.SIGNAL( 'clicked()' ),
                                getattr( self, callback ) )
            self.layout.addWidget( button )

        # Add the x,y location widget at the right side of the toolbar
        # The stretch factor is 1 which means any resizing of the toolbar
        # will resize this label instead of the buttons.
        self.locLabel = QtGui.QLabel( "", self )
        self.locLabel.setAlignment( QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter )
        self.locLabel.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored,
                                                      QtGui.QSizePolicy.Ignored))
        self.layout.addWidget( self.locLabel, 1 )

    def dynamic_update( self ):
        self.canvas.draw()

    def set_message( self, s ):
        self.locLabel.setText( s.replace(', ', '\n') )

    def set_cursor( self, cursor ):
        if DEBUG: print 'Set cursor' , cursor
        QtGui.QApplication.restoreOverrideCursor()
        QtGui.QApplication.setOverrideCursor( QtGui.QCursor( cursord[cursor] ) )
                
    def draw_rubberband( self, event, x0, y0, x1, y1 ):
        height = self.canvas.figure.bbox.height()
        y1 = height - y1
        y0 = height - y0
        
        w = abs(x1 - x0)
        h = abs(y1 - y0)

        rect = [ int(val)for val in min(x0,x1), min(y0, y1), w, h ]
        self.canvas.drawRectangle( rect )
    
    def save_figure( self ):     
        fname = QtGui.QFileDialog.getSaveFileName()
        if fname:
            self.canvas.print_figure( str(fname.toLatin1()) )

def error_msg_qt( msg, parent=None ):
    if not is_string_like( msg ):
        msg = ','.join( map( str,msg ) )
                         
    QtGui.QMessageBox.warning( None, "Matplotlib", msg, QtGui.QMessageBox.Ok )

def exception_handler( type, value, tb ):
    """Handle uncaught exceptions
    It does not catch SystemExit
    """
    msg = ''
    # get the filename attribute if available (for IOError)
    if hasattr(value, 'filename') and value.filename != None:
        msg = value.filename + ': '
    if hasattr(value, 'strerror') and value.strerror != None:
        msg += value.strerror
    else:
        msg += str(value)

    if len( msg ) : error_msg_qt( msg )


FigureManager = FigureManagerQT

# We need one and only one QApplication before we can build any Qt widgets
# Detect if a QApplication exists.
createQApp = QtGui.QApplication.startingUp()
if createQApp:
    if DEBUG: print "Starting up QApplication"
    qtapplication = QtGui.QApplication( [" "] )
