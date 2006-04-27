import sys
import matplotlib

__all__ = ['backend','show','draw_if_interactive',
           'new_figure_manager', 'backend_version']

interactive_bk = ['GTK', 'GTKAgg', 'GTKCairo', 'FltkAgg', 'QtAgg', 'TkAgg', 
                  'WX', 'WXAgg', 'CocoaAgg', 'Aqt']
non_interactive_bk = ['Agg2', 'Agg', 'Cairo', 'EMF', 'GD', 'GDK', 'Paint', 
		      'Pdf', 'PS', 'SVG', 'Template']
all_backends = interactive_bk + non_interactive_bk

backend = matplotlib.get_backend()
if backend not in all_backends:
    raise ValueError, 'Unrecognized backend %s' % backend

def pylab_setup():
    'return new_figure_manager, draw_if_interactive and show for pylab'
    # Import the requested backend into a generic module object

    backend_name = 'backend_'+backend.lower()
    backend_mod = __import__('matplotlib.backends.'+backend_name,
                             globals(),locals(),[backend_name])

    # Things we pull in from all backends
    new_figure_manager = backend_mod.new_figure_manager

    if hasattr(backend_mod,'backend_version'):
        backend_version = getattr(backend_mod,'backend_version')
    else: backend_version = 'unknown'



    # Now define the public API according to the kind of backend in use
    if backend in interactive_bk:
        show = backend_mod.show
        draw_if_interactive = backend_mod.draw_if_interactive
    else:  # non-interactive backends
        def draw_if_interactive():  pass
        def show(): pass

    # Additional imports which only happen for certain backends.  This section
    # should probably disappear once all backends are uniform.
    if backend in ['WX','WXAgg']:
        Toolbar = backend_mod.Toolbar
        __all__.append('Toolbar')

    matplotlib.verbose.report('backend %s version %s' % (backend,backend_version))

    return new_figure_manager, draw_if_interactive, show

# a hack to keep old versions of ipython working with mpl after bug
# fix #1209354
if 'IPython.Shell' in  sys.modules:
    new_figure_manager, draw_if_interactive, show = pylab_setup()

