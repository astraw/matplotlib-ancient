modules = (
    'matplotlib.afm',
    'matplotlib.artist',
    'matplotlib.axes',
    'matplotlib.axis',
    'matplotlib.backend_bases',
    'matplotlib.backends.backend_agg',
    'matplotlib.backends.backend_gd',
    'matplotlib.backends.backend_gtk',
    'matplotlib.backends.backend_gtkagg',
    'matplotlib.backends.backend_paint',
    'matplotlib.backends.backend_ps',
    'matplotlib.backends.backend_svg',    
    'matplotlib.backends.backend_template',
    'matplotlib.backends.backend_tkagg',
    'matplotlib.backends.backend_wx',
    'matplotlib.backends.backend_wxagg',
    'matplotlib.cbook',
    'matplotlib.collections',
    'matplotlib.colors',
    'matplotlib.dates',
    'matplotlib.figure',
    'matplotlib.finance',
    'matplotlib.font_manager',
    'matplotlib.ft2font',
    'matplotlib.image',
    'matplotlib.legend',
    'matplotlib.lines',
    'matplotlib.mathtext',
    'matplotlib.matlab',
    'matplotlib.mlab',
    'matplotlib.numerix',
    'matplotlib.patches',
    'matplotlib.table',
    'matplotlib.text',
    'matplotlib.ticker',
    'matplotlib.transforms' )


def get_mpl_commands():
    """
    return value is a list of (header, commands) where commands is a
    list of (func, desc)
    """
    
    plot_commands = []
    # parse the header for the commands provided commands
    for line in file('../matplotlib/matlab.py'):
        line = line.strip()
        if not len(line): continue
        if line.startswith('__end'): break
        if line.startswith('_'):
            header = line[1:].strip()
            these = []
            plot_commands.append((header, these))
            continue
        tup = line.split('-', 1)
        if len(tup)!=2: continue
        func, desc = tup
        func = func.strip()
        desc = desc.strip()
        these.append((func, desc))                                             
    return plot_commands
