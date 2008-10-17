"""A special directive for including a matplotlib plot.

Given a path to a .py file, it includes the source code inline, then:

- On HTML, will include a .png with a link to a high-res .png.

- On LaTeX, will include a .pdf

This directive supports all of the options of the `image` directive,
except for `target` (since plot will add its own target).

Additionally, if the :include-source: option is provided, the literal
source will be included inline, as well as a link to the source.
"""

import sys, os, glob, shutil, imp, warnings, cStringIO
from docutils.parsers.rst import directives
try:
    # docutils 0.4
    from docutils.parsers.rst.directives.images import align
except ImportError:
    # docutils 0.5
    from docutils.parsers.rst.directives.images import Image
    align = Image.align

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import _pylab_helpers

def runfile(fullpath):
    # Change the working directory to the directory of the example, so
    # it can get at its data files, if any.
    pwd = os.getcwd()
    path, fname = os.path.split(fullpath)
    os.chdir(path)
    stdout = sys.stdout
    sys.stdout = cStringIO.StringIO()
    try:
        fd = open(fname)
        module = imp.load_module("__main__", fd, fname, ('py', 'r', imp.PY_SOURCE))
    except:
        raise
    finally:
        os.chdir(pwd)
        sys.stdout = stdout
    return module

options = {'alt': directives.unchanged,
           'height': directives.length_or_unitless,
           'width': directives.length_or_percentage_or_unitless,
           'scale': directives.nonnegative_int,
           'align': align,
           'class': directives.class_option,
           'include-source': directives.flag }

template = """
.. htmlonly::

   [`source code <%(destdir)s/%(basename)s.py>`__,
   `png <%(destdir)s/%(outname)s.hires.png>`__,
   `pdf <%(destdir)s/%(outname)s.pdf>`__]

   .. image:: %(destdir)s/%(outname)s.png
%(options)s

.. latexonly::
   .. image:: %(destdir)s/%(outname)s.pdf
%(options)s

"""

exception_template = """
.. htmlonly::

   [`source code <%(destdir)s/%(basename)s.py>`__]

Exception occurred rendering plot.

"""


def out_of_date(original, derived):
    """
    Returns True if derivative is out-of-date wrt original,
    both of which are full file paths.
    """
    return (not os.path.exists(derived))
    # or os.stat(derived).st_mtime < os.stat(original).st_mtime)

def makefig(fullpath, outdir):
    """
    run a pyplot script<t and save the low and high res PNGs and a PDF in _static
    """

    fullpath = str(fullpath)  # todo, why is unicode breaking this
    formats = [('png', 100),
               ('hires.png', 200),
               ('pdf', 50),
               ]

    basedir, fname = os.path.split(fullpath)
    basename, ext = os.path.splitext(fname)
    all_exists = True

    if basedir != outdir:
        shutil.copyfile(fullpath, os.path.join(outdir, fname))

    # Look for single-figure output files first
    for format, dpi in formats:
        outname = os.path.join(outdir, '%s.%s' % (basename, format))
        if out_of_date(fullpath, outname):
            all_exists = False
            break

    if all_exists:
        print '    already have %s'%fullpath
        return 1

    # Then look for multi-figure output files, assuming
    # if we have some we have all...
    i = 0
    while True:
        all_exists = True
        for format, dpi in formats:
            outname = os.path.join(outdir, '%s_%02d.%s' % (basename, i, format))
            if out_of_date(fullpath, outname):
                all_exists = False
                break
        if all_exists:
            i += 1
        else:
            break

    if i != 0:
        print '    already have %d figures for %s' % (i, fullpath)
        return i

    # We didn't find the files, so build them

    print '    building %s'%fullpath
    plt.close('all')    # we need to clear between runs
    matplotlib.rcdefaults()
    # Set a figure size that doesn't overflow typical browser windows
    matplotlib.rcParams['figure.figsize'] = (6.5, 4.5)

    try:
        runfile(fullpath)
    except:
        warnings.warn("Exception running plot %s" % fullpath)
        return 0

    fig_managers = _pylab_helpers.Gcf.get_all_fig_managers()
    for i, figman in enumerate(fig_managers):
        for format, dpi in formats:
            if len(fig_managers) == 1:
                outname = basename
            else:
                outname = "%s_%02d" % (basename, i)
            outpath = os.path.join(outdir, '%s.%s' % (outname, format))
            try:
                figman.canvas.figure.savefig(outpath, dpi=dpi)
            except:
                warnings.warn("Exception running plot %s" % fullpath)
                return 0

    return len(fig_managers)

def run(arguments, options, state_machine, lineno):
    reference = directives.uri(arguments[0])
    basedir, fname = os.path.split(reference)
    basename, ext = os.path.splitext(fname)

    destdir = ('../' * reference.count('/')) + 'pyplots'
    num_figs = makefig(reference, 'pyplots')

    if options.has_key('include-source'):
        contents = open(reference, 'r').read()
        lines = ['::', ''] + ['    %s'%row.rstrip() for row in contents.split('\n')]
        del options['include-source']
    else:
        lines = []

    if num_figs > 0:
        options = ['      :%s: %s' % (key, val) for key, val in
                   options.items()]
        options = "\n".join(options)

        for i in range(num_figs):
            if num_figs == 1:
                outname = basename
            else:
                outname = "%s_%02d" % (basename, i)
            lines.extend((template % locals()).split('\n'))
    else:
        lines.extend((exception_template % locals()).split('\n'))

    if len(lines):
        state_machine.insert_input(
            lines, state_machine.input_lines.source(0))
    return []

try:
    from docutils.parsers.rst import Directive
except ImportError:
    from docutils.parsers.rst.directives import _directives

    def plot_directive(name, arguments, options, content, lineno,
                       content_offset, block_text, state, state_machine):
        return run(arguments, options, state_machine, lineno)
    plot_directive.__doc__ = __doc__
    plot_directive.arguments = (1, 0, 1)
    plot_directive.options = options

    _directives['plot'] = plot_directive
else:
    class plot_directive(Directive):
        required_arguments = 1
        optional_arguments = 0
        final_argument_whitespace = True
        option_spec = options
        def run(self):
            return run(self.arguments, self.options,
                       self.state_machine, self.lineno)
    plot_directive.__doc__ = __doc__

    directives.register_directive('plot', plot_directive)

