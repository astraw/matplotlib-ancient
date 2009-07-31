#!/usr/bin/env python
"""
This is used to drive many of the examples across the backends, for
regression testing, and comparing backend efficiency.

You can specify the backends to be tested either via the --backends
switch, which takes a comma-separated list, or as separate arguments,
e.g.

    python backend_driver.py agg ps cairo.png cairo.ps

would test the agg and ps backends, and the cairo backend with output
to png and ps files. If no arguments are given, a default list of
backends will be tested.

Interspersed with the backend arguments can be switches for the Python
interpreter executing the tests. If entering such arguments causes an
option parsing error with the driver script, separate them from driver
switches with a --.
"""

from __future__ import division
import os, time, sys, glob, string
from optparse import OptionParser
import matplotlib.rcsetup as rcsetup
from matplotlib.cbook import Bunch, dedent

all_backends = list(rcsetup.all_backends)  # to leave the original list alone
all_backends.extend(['cairo.png', 'cairo.ps', 'cairo.pdf', 'cairo.svg'])

# actual physical directory for each dir
dirs = dict(pylab = os.path.join('..', 'pylab_examples'),
            api = os.path.join('..', 'api'),
            units = os.path.join('..', 'units'),
            mplot3d = os.path.join('..', 'mplot3d'))

# files in each dir
files = dict()
files['pylab'] = [
    'accented_text.py',
    'alignment_test.py',
    'annotation_demo.py',
    'annotation_demo.py',
    'annotation_demo2.py',
    'annotation_demo2.py',
    'anscombe.py',
    'arctest.py',
    'arrow_demo.py',
    'axes_demo.py',
    'axes_props.py',
    'axhspan_demo.py',
    'axis_equal_demo.py',
    'bar_stacked.py',
    'barb_demo.py',
    'barchart_demo.py',
    'barcode_demo.py',
    'barh_demo.py',
    'boxplot_demo.py',
    'broken_barh.py',
    'clippedline.py',
    'cohere_demo.py',
    'color_by_yvalue.py',
    'color_demo.py',
    'colorbar_tick_labelling_demo.py',
    'contour_demo.py',
    'contour_image.py',
    'contour_label_demo.py',
    'contourf_demo.py',
    'contourf_log.py',
    'coords_demo.py',
    'coords_report.py',
    'csd_demo.py',
    'cursor_demo.py',
    'custom_cmap.py',
    'custom_figure_class.py',
    'custom_ticker1.py',
    'customize_rc.py',
    'dash_control.py',
    'dashpointlabel.py',
    'date_demo1.py',
    'date_demo2.py',
    'date_demo_convert.py',
    'date_demo_rrule.py',
    'date_index_formatter.py',
    'dolphin.py',
    'ellipse_collection.py',
    'ellipse_demo.py',
    'ellipse_rotated.py',
    'equal_aspect_ratio.py',
    'errorbar_demo.py',
    'errorbar_limits.py',
    'fancyarrow_demo.py',
    'fancybox_demo.py',
    'fancybox_demo2.py',
    'fancytextbox_demo.py',
    'figimage_demo.py',
    'figlegend_demo.py',
    'figure_title.py',
    'fill_between_demo.py',
    'fill_demo.py',
    'fill_demo2.py',
    'fill_spiral.py',
    'finance_demo.py',
    'findobj_demo.py',
    'fonts_demo.py',
    'fonts_demo_kw.py',
    'ganged_plots.py',
    'geo_demo.py',
    'gradient_bar.py',
    'griddata_demo.py',
    'hatch_demo.py',
    'hexbin_demo.py',
    'hexbin_demo2.py',
    'hist_colormapped.py',
    'histogram_demo.py',
    'histogram_demo_extended.py',
    'hline_demo.py',

    'image_clip_path.py',
    'image_demo.py',
    'image_demo2.py',
    'image_demo3.py',
    'image_interp.py',
    'image_masked.py',
    'image_nonuniform.py',
    'image_origin.py',
    'image_slices_viewer.py',
    'integral_demo.py',
    'interp_demo.py',
    'invert_axes.py',
    'layer_images.py',
    'legend_auto.py',
    'legend_demo.py',
    'legend_demo2.py',
    'legend_demo3.py',
    'legend_scatter.py',
    'line_collection.py',
    'line_collection2.py',
    'line_styles.py',
    'log_bar.py',
    'log_demo.py',
    'log_test.py',
    'major_minor_demo1.py',
    'major_minor_demo2.py',
    'manual_axis.py',
    'masked_demo.py',
    'mathtext_demo.py',
    'mathtext_examples.py',
    'matplotlib_icon.py',
    'matshow.py',
    'mri_demo.py',
    'mri_with_eeg.py',
    'multi_image.py',
    'multiline.py',
    'multiple_figs_demo.py',
    'nan_test.py',
    'newscalarformatter_demo.py',
    'pcolor_demo.py',
    'pcolor_demo2.py',
    'pcolor_log.py',
    'pcolor_small.py',
    'pie_demo.py',
    'plotfile_demo.py',
    'polar_bar.py',
    'polar_demo.py',
    'polar_legend.py',
    'polar_scatter.py',
    'poormans_contour.py',
    'psd_demo.py',
    'psd_demo2.py',
    'psd_demo3.py',
    'quadmesh_demo.py',
    'quiver_demo.py',
    'scatter_custom_symbol.py',
    'scatter_demo.py',
    'scatter_demo2.py',
    'scatter_masked.py',
    'scatter_profile.py',
    'scatter_star_poly.py',
    #'set_and_get.py',
    'shared_axis_across_figures.py',
    'shared_axis_demo.py',
    'simple_plot.py',
    'simplification_clipping_test.py',
    'specgram_demo.py',
    'spine_placement_demo.py',
    'spy_demos.py',
    'stem_plot.py',
    'step_demo.py',
    'stix_fonts_demo.py',
    'stock_demo.py',
    'subplot_demo.py',
    'subplots_adjust.py',
    'symlog_demo.py',
    'table_demo.py',
    'text_handles.py',
    'text_rotation.py',
    'text_rotation_relative_to_line.py',
    'text_themes.py',
    'transoffset.py',
    'unicode_demo.py',
    'vertical_ticklabels.py',
    'vline_demo.py',
    'xcorr_demo.py',
    'zorder_demo.py',
    ]


files['api'] = [
    'agg_oo.py',
    'barchart_demo.py',
    'bbox_intersect.py',
    'collections_demo.py',
    'color_cycle.py',
    'colorbar_only.py',
    'custom_projection_example.py',
    'custom_scale_example.py',
    'date_demo.py',
    'date_index_formatter.py',
    'donut_demo.py',
    'font_family_rc.py',
    'histogram_demo.py',
    'image_zcoord.py',
    'joinstyle.py',
    'legend_demo.py',
    'line_with_text.py',
    'logo2.py',
    'mathtext_asarray.py',
    'patch_collection.py',
    'path_patch_demo.py',
    'quad_bezier.py',
    'scatter_piecharts.py',
    'span_regions.py',
    'two_scales.py',
    'unicode_minus.py',
    'watermark_image.py',
    'watermark_text.py',
]

files['units'] = [
    'annotate_with_units.py',
    #'artist_tests.py',  # broken, fixme
    'bar_demo2.py',
    #'bar_unit_demo.py', # broken, fixme
    #'ellipse_with_units.py',  # broken, fixme
    'radian_demo.py',
    'units_sample.py',
    #'units_scatter.py', # broken, fixme

    ]

files['mplot3d'] = [
    '2dcollections3d_demo.py',
    'bars3d_demo.py',
    'contour3d_demo.py',
    'contour3d_demo2.py',
    'contourf3d_demo.py',
    'lines3d_demo.py',
    'polys3d_demo.py',
    'scatter3d_demo.py',
    'surface3d_demo.py',
    'surface3d_demo2.py',
    'text3d_demo.py',
    'wire3d_demo.py',
    ]

# dict from dir to files we know we don't want to test (eg examples
# not using pyplot, examples requiring user input, animation examples,
# examples that may only work in certain environs (usetex examples?),
# examples that generate multiple figures

excluded = {
    'pylab' : ['__init__.py', 'toggle_images.py',],
    'units' : ['__init__.py', 'date_support.py',],
}

def report_missing(dir, flist):
    'report the py files in dir that are not in flist'
    globstr = os.path.join(dir, '*.py')
    fnames = glob.glob(globstr)

    pyfiles = set([os.path.split(fullpath)[-1] for fullpath in set(fnames)])

    exclude = set(excluded.get(dir, []))
    flist = set(flist)
    missing = list(pyfiles-flist-exclude)
    missing.sort()
    if missing:
        print '%s files not tested: %s'%(dir, ', '.join(missing))

def report_all_missing(directories):
    for f in directories:
        report_missing(dirs[f], files[f])


# tests known to fail on a given backend

failbackend = dict(
    svg = ('tex_demo.py', ),
    agg = ('hyperlinks.py', ),
    pdf = ('hyperlinks.py', ),
    ps = ('hyperlinks.py', ),
    )


try:
    import subprocess
    def run(arglist):
        try:
            ret = subprocess.call(arglist)
        except KeyboardInterrupt:
            sys.exit()
        else:
            return ret
except ImportError:
    def run(arglist):
        os.system(' '.join(arglist))

def drive(backend, directories, python=['python'], switches = []):
    exclude = failbackend.get(backend, [])

    # Clear the destination directory for the examples
    path = backend
    if os.path.exists(path):
        import glob
        for fname in os.listdir(path):
            os.unlink(os.path.join(path,fname))
    else:
        os.mkdir(backend)
    failures = []

    testcases = [os.path.join(dirs[d], fname)
                 for d in directories
                 for fname in files[d]]

    for fullpath in testcases:
        print ('\tdriving %-40s' % (fullpath)),
        sys.stdout.flush()

        fpath, fname = os.path.split(fullpath)

        if fname in exclude:
            print '\tSkipping %s, known to fail on backend: %s'%backend
            continue

        basename, ext = os.path.splitext(fname)
        outfile = os.path.join(path,basename)
        tmpfile_name = '_tmp_%s.py' % basename
        tmpfile = file(tmpfile_name, 'w')

        for line in file(fullpath):
            line_lstrip = line.lstrip()
            if line_lstrip.startswith("#"):
                tmpfile.write(line)
            else:
                break

        tmpfile.writelines((
            'from __future__ import division\n',
            'import sys\n',
            'sys.path.append("%s")\n'%fpath,
            'import matplotlib\n',
            'matplotlib.use("%s")\n' % backend,
            'from pylab import savefig\n',
            ))
        for line in file(fullpath):
            line_lstrip = line.lstrip()
            if (line_lstrip.startswith('from __future__ import division') or
                line_lstrip.startswith('matplotlib.use') or
                line_lstrip.startswith('savefig') or
                line_lstrip.startswith('show')):
                continue
            tmpfile.write(line)
        if backend in rcsetup.interactive_bk:
            tmpfile.write('show()')
        else:
            tmpfile.write('\nsavefig("%s", dpi=150)' % outfile)

        tmpfile.close()
        start_time = time.time()
        program = [x % {'name': basename} for x in python]
        ret = run(program + [tmpfile_name] + switches)
        end_time = time.time()
        print (end_time - start_time), ret
        #os.system('%s %s %s' % (python, tmpfile_name, ' '.join(switches)))
        os.remove(tmpfile_name)
        if ret:
            failures.append(fullpath)
    return failures

def parse_options():
    doc = __doc__.split('\n\n')
    op = OptionParser(description=doc[0].strip(),
                      usage='%prog [options] [--] [backends and switches]',
                      #epilog='\n'.join(doc[1:])  # epilog not supported on my python2.4 machine: JDH
                      )
    op.disable_interspersed_args()
    op.set_defaults(dirs='pylab,api,units,mplot3d',
                    clean=False, coverage=False, valgrind=False)
    op.add_option('-d', '--dirs', '--directories', type='string',
                  dest='dirs', help=dedent('''
      Run only the tests in these directories; comma-separated list of
      one or more of: pylab (or pylab_examples), api, units, mplot3d'''))
    op.add_option('-b', '--backends', type='string', dest='backends',
                  help=dedent('''
      Run tests only for these backends; comma-separated list of
      one or more of: agg, ps, svg, pdf, template, cairo,
      cairo.png, cairo.ps, cairo.pdf, cairo.svg. Default is everything
      except cairo.'''))
    op.add_option('--clean', action='store_true', dest='clean',
                  help='Remove result directories, run no tests')
    op.add_option('-c', '--coverage', action='store_true', dest='coverage',
                  help='Run in coverage.py')
    op.add_option('-v', '--valgrind', action='store_true', dest='valgrind',
                  help='Run in valgrind')

    options, args = op.parse_args()
    switches = [x for x in args if x.startswith('--')]
    backends = [x.lower() for x in args if not x.startswith('--')]
    if options.backends:
        backends += map(string.lower, options.backends.split(','))

    result = Bunch(
        dirs = options.dirs.split(','),
        backends = backends or ['agg', 'ps', 'svg', 'pdf', 'template'],
        clean = options.clean,
        coverage = options.coverage,
        valgrind = options.valgrind,
        switches = switches)
    if 'pylab_examples' in result.dirs:
        result.dirs[result.dirs.index('pylab_examples')] = 'pylab'
    #print result
    return result

if __name__ == '__main__':
    times = {}
    failures = {}
    options = parse_options()

    if options.clean:
        localdirs = [d for d in glob.glob('*') if os.path.isdir(d)]
        all_backends_set = set(all_backends)
        for d in localdirs:
            if d.lower() not in all_backends_set:
                continue
            print 'removing %s'%d
            for fname in glob.glob(os.path.join(d, '*')):
                os.remove(fname)
            os.rmdir(d)
        for fname in glob.glob('_tmp*.py'):
            os.remove(fname)

        print 'all clean...'
        raise SystemExit
    if options.coverage:
        python = ['coverage.py', '-x']
    elif options.valgrind:
        python = ['valgrind', '--tool=memcheck', '--leak-check=yes',
                  '--log-file=%(name)s', 'python']
    elif sys.platform == 'win32':
        python = [r'c:\Python24\python.exe']
    else:
        python = ['python']

    report_all_missing(options.dirs)
    for backend in options.backends:
        print 'testing %s %s' % (backend, ' '.join(options.switches))
        t0 = time.time()
        failures[backend] = \
            drive(backend, options.dirs, python, options.switches)
        t1 = time.time()
        times[backend] = (t1-t0)/60.0

    # print times
    for backend, elapsed in times.items():
        print 'Backend %s took %1.2f minutes to complete' % (backend, elapsed)
        failed = failures[backend]
        if failed:
            print '  Failures: ', failed
        if 'template' in times:
            print '\ttemplate ratio %1.3f, template residual %1.3f' % (
                elapsed/times['template'], elapsed-times['template'])
