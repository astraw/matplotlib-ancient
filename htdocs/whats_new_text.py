# paste in the what's new from whats_new.html.template and run this script

whatsnew = (
('Font handling',
"""
Major improvements in font and text handling.  matplotlib 0.1 drew all
text in the same, non-configurable font.  In 0.2, font name, size,
weight, and angle, color, rotation, and more are easily configurable.
See the <a href=tutorial.html#text>text tutorial</a>.
"""),

('Multiple figures',
"""
Multiple figures supported with the figure command.  See the <a
href=tutorial.html#figs_and_axes>Working with multiple figures and
axes</a>.
"""),

('Interactive shell',
"""
Interactive use from the python shell if you have pygtk compiled with
threads.  See <a href=interactive.html>Using matplotlib
interactively</a>.
"""),

('Saving figures',
"""
Ability to save figures in arbitrary resolution PNG or TIFF with a bug
fix that caused saved figures to be corrupted by anything blocking the
figure window.  A GUI widget has been added to the figure toolbar to
save figures and a new comand <a href=matplotlib.matlab.html#-savefig>savefig</a>
has been added.
"""),

('Navigation',
"""
A new and hopefully improved navigation toolbar has been added that
doesn't require a wheel mouse, but still works with one.  See <a
href=tutorial.html#navigation>the Navigation tutorial</a>.
"""),

('More examples and screenshots',
"""
New examples and screenshot illustrating the new text functionality,
the new plot types, and new commands.  See the examples subdirectory
in the src distribution.
"""),

('Patches',
"""
A <a href=patches.html#Patch>Patch</a> class added for drawing patches
(rectangles, polygons, circles).  This supports three new plotting
commands <a href=matplotlib.matlab.html#-scatter>scatter</a>, <a
href=matlab.html#-hist>hist</a> and <a href=matplotlib.matlab.html#-bar>bar</a>,
with more to come.
"""),

('New commands',
"""
New plotting commands <a href=matplotlib.matlab.html#-bar>bar</a>, <a href=matplotlib.matlab.html#-close>close</a>, <a href=matplotlib.matlab.html#-errorbar>errorbar</a>, <a href=matplotlib.matlab.html#-figure>figure</a>, <a href=matplotlib.matlab.html#-hist>hist</a>, <a href=matplotlib.matlab.html#-text>text</a>,
  <a href=matplotlib.matlab.html#-scatter>scatter</a>, <a href=matplotlib.matlab.html#-savefig>savefig</a>, <a href=matplotlib.matlab.html#-ylabel>ylabel</a>.
"""),

('Matplotlib on sourceforge',
"""
matplotlib homepage moved to <a
href=http://matplotlib.sourceforge.net>sourceforge</a> with a
(hopefully) more useful homepage.
"""),

('Documentation',
"""
Much better documentation and a <a href=tutorial.html>tutorial</a>.
"""),

('Refactoring',
"""
Substantial rewrite of class library.  All text now handled by the <a
href=text.html#AxisText>AxisText</a> class in text.py.  Axis handling
refactored into dedicated class <a href=figure.html#Axis>Axis</a>
defined in figure.py.
"""),


)

for title, new in whatsnew:
    print title, '-', 
    
