import os
files = (
    'alignment_demo.py',
    'axes_demo.py',
    'compare_with_matlab.py',
    'color_demo.py',            
    'date_ticker_demo.py',
    'figure_mosaic.py',
    'fonts_demo_kw.py',
    'from_pil.py',
    'image_demo.py',
    'image_origin.py',
    'integral_demo.py',    
    'layer_images.py',
    'linear_regression.py',
    'major_minor_demo.py',
    'mathtext_demo.py',
    'poly_regression.py',
    'simple_imshow.py',
    'simple_plot_tkagg.py',
    'specgram_demo.py',
    'subplot_demo.py',
    )

for fname in files:
    print 'Running', fname
    os.system('python %s' % fname)
    


"""
simple_plot_tkagg.png
simple_plot_tkagg_labeled.png
simple_plot_tkagg_sine.png
simple_plot_tkagg.eps
simple_plot_tkagg_labeled.eps
simple_plot_tkagg_sine.eps
"""
