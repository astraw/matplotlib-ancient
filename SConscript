import os
import sys

from numscons import GetNumpyEnvironment

from setupext import options, print_message, find_wx_config, check_for_macosx

# XXX: stuff copied from setupext/setup
# This dict will be updated as we try to select the best option during
# the build process. However, values in setup.cfg will be used, if
# defined.
rc = {'backend':'Agg'}

AGG_VERSION = 'agg24'

env = GetNumpyEnvironment(ARGUMENTS)

def merge_build_dict(d1, d2):
    """Merge d2 'into' d1."""
    for k, v in d2.items():
        if v:
            d1[k].append(v)

    return d1

def try_build(context, src, build_info, autoadd):
    from numscons.checkers.common import save_and_set, restore

    st = 0
    saved = save_and_set(context.env, build_info)
    try:
        # Return 1 if *successful*
        st = context.TryLink(src % str(build_info), '.c')
    finally:
        if st == 0 or autoadd == 0:
            restore(context.env, saved)

    if not st:
        context.Result('Failed: check config.log in %s for more details' \
            % context.env['build_dir'])
    else:
        context.Result('Yes')

    return st

def check_from_section(context, section, config, src, default_dict, autoadd):
    from numscons.checkers.config import BuildDict
    build_info = BuildDict.from_config_dict(config)
    if build_info['LIBS'] is None:
        build_info['LIBS'] = default_dict['LIBS']

    return try_build(context, src, build_info, autoadd)

def check_from_pkg_config(context, cmd_base, src, autoadd):
    if sys.platform == 'win32':
        raise NotImplementedError("Win32 support for pkg-config not implemented yet")
    else:
        cflags_cmd = [cmd_base]
        cflags_cmd.append('--cflags')
        compile_info = context.env.ParseFlags([' '.join(cflags_cmd)])

        link_cmd = [cmd_base]
        link_cmd.append('--libs')
        link_info = context.env.ParseFlags([' '.join(link_cmd)])

        build_info = merge_build_dict(compile_info, link_info)

        return try_build(context, src, build_info, autoadd)

def CheckFreeType(context, autoadd=1):
    from numscons.checkers.config import _read_section, BuildDict

    context.Message("Checking for freetype2 ... ")

    section = 'freetype2'
    pkg_config_cmd = ['freetype-config']
    pkg_config_name = None
    libs = ['freetype', 'z']
    headers = ['ft2build.h']

    default_build_info = BuildDict()
    default_build_info['LIBS'] = libs

    return _GenericCheck(context, section, headers, default_build_info,
                         pkg_config_cmd, autoadd=autoadd)

def CheckPng(context, autoadd=1):
    from numscons.checkers.config import _read_section, BuildDict

    context.Message("Checking for png ... ")

    section = 'png'
    headers = ['png.h']

    default_build_info = BuildDict()
    default_build_info['LIBS'] = ['png']

    return _GenericCheck(context, section, headers, default_build_info,
                         autoadd=autoadd)

def CheckPyGTK(context, autoadd=1):
    from numscons.checkers.config import _read_section, BuildDict

    version = (2,2,0)
    pkg_config_cmd = ['pkg-config', 'pygtk-2.0', 'gtk+-2.0']

    context.Message("Checking for pygtk >= %s ... " % str(version))

    explanation = None
    try:
        import gtk
    except ImportError:
        explanation = 'could not import gtk in python'
    except RuntimeError:
        explanation = 'pygtk present but import failed'
    else:
        if gtk.pygtk_version < version:
            explanation = "%d.%d.%d was detected." % gtk.pygtk_version

    if explanation is not None:
        context.Result(explanation)
        return 0

    section = 'gtk'
    headers = ['gtk/gtk.h']

    default_build_info = BuildDict()
    default_build_info['LIBS'] = ['gtk']

    st = _GenericCheck(context, section, headers, default_build_info,
                       pkg_config_cmd, autoadd=autoadd)
    if st:
        try:
            gtk.set_interactive(False)
        except AttributeError: # PyGTK < 2.15.0
            pass
    return st

def CheckWxPython(context, autoadd=1):
    from numscons.checkers.config import _read_section, BuildDict

    version = (2,8)
    strversion = ".".join([str(i) for i in version])
    pkg_config_cmd = ['wx-config']

    context.Message("Checking for wxpython ... ")

    explanation = None
    try:
        import wx
    except ImportError:
        explanation = 'wxPython not found'
    else:
        if getattr(wx, '__version__', '0.0')[0:3] >= strversion:
            context.Result(wx.__version__)
            return 1
        else:
            # TODO: mingw-win32 checks + broken macosx version
            wx_config = find_wx_config()
            if wx_config:
                default_build_info = BuildDict()
                default_build_info['LIBS'] = ['gtk']

                return _GenericCheck(context, 'wxpython',
                    default_build_info=default_build_info,
                    pkg_config_cmd = [wx_config], autoadd=autoadd)

    if explanation is not None:
        context.Result(explanation)
        return 0
    else:
        context.Result('Yes')
        return 1

def _GenericCheck(context, section, headers=None, default_build_info=None,
        pkg_config_cmd=None, autoadd=1):
    # pkg_config_cmd should be a sequence
    from numscons.checkers.config import _read_section, BuildDict

    if default_build_info is None:
        default_build_info = BuildDict()

    if headers:
        src = [r"#include <%s>" % h for h in headers]
    else:
        src = [""]

    src.append(r"""
int main(void)
{
    return 0;
}
#if 0
%s
#endif
""")

    src = "\n".join(src)

    # Test using user configuration (numscons.cfg)
    config = _read_section(section, context.env)
    if config:
        return check_from_section(context, section, config, src,
                default_build_info, autoadd=autoadd)

    # Test using pkg-config
    if pkg_config_cmd:
        cmd_base = '!%s' % " ".join(pkg_config_cmd)
        return check_from_pkg_config(context, cmd_base, src, autoadd=autoadd)

    # Conventional test (using default config)
    return try_build(context, src, default_build_info, autoadd=autoadd)

#------------------------
# Configuration checks
#------------------------
custom_tests = {'CheckFreeType': CheckFreeType, 'CheckPng': CheckPng,
    'CheckPyGTK': CheckPyGTK, 'CheckWxPython': CheckWxPython}

config = env.NumpyConfigure(custom_tests=custom_tests)
if not config.CheckFreeType():
    print_message("Cannot build matplotlib without freetype2.")
    sys.exit(-1)

has_libpng = True
if not config.CheckPng():
    has_libpng = False

has_pygtk = True
if not config.CheckPyGTK():
    has_pygtk = False

has_wxpython = True
if not config.CheckWxPython():
    has_wxpython = False

config.Finish()

#---------------
# Common builds
#---------------
env.Append(CPPPATH=["%s/include" % AGG_VERSION, "."])
env.Append(CPPDEFINES=[("PY_ARRAY_UNIQUE_SYMBOL", "MPL_ARRAY_API")])
npenv = env.Clone()
npenv.Append(CPPPATH=env['NUMPYCPPPATH'])

common_cxx = [env.PythonObject(i) for i in env.Glob("CXX/*.cxx")]
common_c = [env.PythonObject(i) for i in env.Glob('CXX/*.c')]
mplutils = env.PythonObject('src/mplutils.cpp', CXXFILESUFFIX='.cpp')

src = ['src/ft2font.cpp']
src.extend(mplutils + common_cxx + common_c)
env.NumpyPythonExtension("ft2font", source=src, CXXFILESUFFIX=".cpp")

src = ['src/_ttconv.cpp', 'ttconv/pprdrv_tt.cpp', 'ttconv/pprdrv_tt2.cpp',
    'ttconv/ttutil.cpp']
env.NumpyPythonExtension("ttconv", source=src, CXXFILESUFFIX=".cpp")

env.NumpyPythonExtension("_cntr", source="src/cntr.c")

src = ["_delaunay.cpp", "VoronoiDiagramGenerator.cpp",
       "delaunay_utils.cpp", "natneighbors.cpp"]
src = [os.path.join('lib/matplotlib/delaunay',s) for s in src]
env.NumpyPythonExtension("_delaunay", source=src, CXXFILESUFFIX=".cpp")

src = "src/nxutils.c"
env.NumpyPythonExtension('nxutils', source=src)

agg_curves = env.PythonObject('%s/src/agg_curves.cpp' % AGG_VERSION,
                              CXXFILESUFFIX='.cpp')
agg_bezier_arc = env.PythonObject('%s/src/agg_bezier_arc.cpp' % AGG_VERSION,
                                   CXXFILESUFFIX='.cpp')
agg_trans_affine = env.PythonObject('%s/src/agg_trans_affine.cpp' % AGG_VERSION,
                                    CXXFILESUFFIX='.cpp')
agg_vcgen_stroke = env.PythonObject('%s/src/agg_vcgen_stroke.cpp' % AGG_VERSION,
                                    CXXFILESUFFIX='.cpp')
agg_image_filters = env.PythonObject('%s/src/agg_image_filters.cpp' % AGG_VERSION,
                                    CXXFILESUFFIX='.cpp')
agg_vcgen_dash = env.PythonObject('%s/src/agg_vcgen_dash.cpp' % AGG_VERSION,
                                    CXXFILESUFFIX='.cpp')
common_agg = agg_curves + agg_bezier_arc + agg_trans_affine + agg_vcgen_stroke

agg_py_transform = npenv.PythonObject('src/agg_py_transforms.cpp', CXXFILESUFFIX='.cpp')

src = common_cxx + common_c + common_agg + agg_py_transform

src.extend(['src/path_cleanup.cpp', 'src/_path.cpp'])
env.NumpyPythonExtension('_path', source=src, CXXFILESUFFIX=".cpp")

#-----------------------
# Optional components
#-----------------------
def build_agg():
    src = agg_trans_affine + agg_bezier_arc + agg_curves + agg_vcgen_dash + \
          agg_vcgen_stroke + agg_image_filters
    src.extend(mplutils)
    src.extend(agg_py_transform)
    src.extend(common_cxx + common_c)
    src.append('src/_backend_agg.cpp')
    env.NumpyPythonExtension('backends/_backend_agg', source=src, CXXFILESUFFIX=".cpp")

def build_image():
    src = mplutils + ['src/_image.cpp']
    src.extend(agg_trans_affine + agg_image_filters + agg_bezier_arc)
    src.extend(common_cxx + common_c)
    env.NumpyPythonExtension('_image', source=src, CXXFILESUFFIX=".cpp")

def build_png():
    src = ['src/_png.cpp']
    src.extend(mplutils + common_c + common_cxx)
    env.NumpyPythonExtension('_png', source=src, CXXFILESUFFIX='.cpp')

def build_gtkagg():
    src = ['src/_gtkagg.cpp']
    src.extend(mplutils + agg_py_transform + common_c + common_cxx)
    env.NumpyPythonExtension('backends/_gtkagg', source=src, CXXFILESUFFIX='.cpp')

if has_libpng and options['build_agg']:
    build_agg()
    rc['backend'] = 'Agg'
else:
    rc['backend'] = 'SVG'

if has_libpng and options['build_image']:
    build_image()

if has_libpng and options['build_agg'] or options['build_image']:
    build_png()

if options['build_windowing'] and sys.platform=='win32':
    print "---- Missing: build_windowing ----"

if options['build_tkagg']:
    print "---- Missing: build_tkagg ----"

if options['build_wxagg']:
    if has_wxpython or (options['build_wxagg'] is True):
        options['build_agg'] = 1
        import wx
        if getattr(wx, '__version__', '0.0')[0:3] < '2.8' :
            print "---- Missing: build_wxagg ----"
            wxagg_backend_status = "yes"
        else:
            print_message("WxAgg extension not required for wxPython >= 2.8")
        rc['backend'] = 'WXAgg'

if options['build_gtk']:
    if has_pygtk or (options['build_gtk'] is True):
        env.NumpyPythonExtension('backends/_backend_gdk',
                                 source=['src/_backend_gdk.c'])

if options['build_gtkagg']:
    if has_pygtk or (options['build_gtkagg'] is True):
        options['build_agg'] = 1
        build_gtkagg()
        rc['backend'] = 'GTKAgg'

if options['build_macosx']:
    if check_for_macosx() or (options['build_macosx'] is True):
        print "---- Missing: build_macosx ----"
        rc['backend'] = 'MacOSX'
