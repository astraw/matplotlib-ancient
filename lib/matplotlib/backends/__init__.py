
import matplotlib
from matplotlib.rcsetup import interactive_bk
from matplotlib.rcsetup import non_interactive_bk
from matplotlib.rcsetup import all_backends
from matplotlib.rcsetup import validate_backend

__all__ = ['backend','show','draw_if_interactive',
           'new_figure_manager', 'backend_version']

backend = matplotlib.get_backend() # validates, to match all_backends

def pylab_setup():
    'return new_figure_manager, draw_if_interactive and show for pylab'
    # Import the requested backend into a generic module object

    backend_name = 'backend_'+backend
    backend_name = backend_name.lower() # until we banish mixed case
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
    if backend.lower() in ['wx','wxagg']:
        Toolbar = backend_mod.Toolbar
        __all__.append('Toolbar')

    matplotlib.verbose.report('backend %s version %s' % (backend,backend_version))

    return new_figure_manager, draw_if_interactive, show


