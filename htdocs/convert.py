import yaptu
import re, os, sys, copy
from StringIO import StringIO

rex=re.compile('@([^@]+)@')
rbe=re.compile('\s*\+')
ren=re.compile('\s*-')
rco=re.compile('\s*= ')

        
class LinkBox:
    def __init__(self, header, links):
        self.header = header
        self.links = links

    def format_header(self):
        return """
    <tr><td  bgcolor=#bfbfbf align="left">
        <font class="tableheading">
                <b>%s</b>
        </font>
    </td></tr>
    """ % self.header
            

    def __repr__(self):
        s =  '<table width=100% border=1 cellpadding=1 ' +\
               'cellspacing=1>\n'
        s += self.format_header()
        s += '  <tr><td valign="top" bgcolor=#efefef>\n'
        for text, link in self.links:
            s += '    <a href=%s>%s</a><br>\n' % (link, text)
            
        s += '</td></tr>\n'
        s += '</table>\n'
        return s

table1 =  LinkBox(header='Matplotlib', links=(
    ('Home', 'http://matplotlib.sourceforge.net'),
    ('Download', 'http://sourceforge.net/projects/matplotlib'),
    ('Installing', 'installing.html'),
    ('Screenshots', 'screenshots.html'),
    ("What's&nbsp;New", 'whats_new.html'),
    ('Mailing lists', 'http://sourceforge.net/mail/?group_id=80706'),
    ))

table2 =  LinkBox(header='Documentation', links=(
    ('Tutorial', 'tutorial.html'),
    ('FAQ', 'faq.html'),    
    ('Matlab&nbsp;interface', 'matlab_commands.html'),
    ('Class&nbsp;library', 'classdocs.html'),
    ('Output formats', 'backends.html'),
    ('Fonts', 'fonts.html'),
    ('Interactive', 'interactive.html'),
    ('Goals', 'goals.html'),
    ))

table3 =  LinkBox(header='Other', links=(
    ('Credits', 'credits.html'),
    ('License', 'license.html'),
    ))


params = {
    'myemail' : '<a href=mailto:jdhunter@ace.bsd.uchicago.edu> (jdhunter@ace.bsd.uchicago.edu)</a>',
    'tables' : (table1, table2, table3),
    'default_table' :  'border=1 cellpadding=3 cellspacing=2', 
          }

headerBuffer = StringIO()
cop = yaptu.copier(rex, params, rbe, ren, rco, ouf=headerBuffer)
lines = file('header.html.template').readlines()
cop.copy(lines)
params['header'] = headerBuffer.getvalue()

footerBuffer = StringIO()
cop = yaptu.copier(rex, params, rbe, ren, rco, ouf=footerBuffer)
lines = file('footer.html.template').readlines()
cop.copy(lines)
params['footer'] = footerBuffer.getvalue()

docs = (
    'matplotlib.afm.html.template',
    'matplotlib.artist.html.template',
    'matplotlib.axes.html.template',
    'matplotlib.axis.html.template',        
    'matplotlib.backend_bases.html.template',
    'matplotlib.backends.backend_agg.html.template',
    'matplotlib.backends.backend_gd.html.template',
    'matplotlib.backends.backend_gtk.html.template',
    'matplotlib.backends.backend_gtkgd.html.template',
    'matplotlib.backends.backend_paint.html.template',
    'matplotlib.backends.backend_ps.html.template',
    'matplotlib.backends.backend_template.html.template',
    'matplotlib.backends.backend_wx.html.template',
    'matplotlib.colors.html.template',
    'matplotlib.cbook.html.template',
    'matplotlib.figure.html.template',        
    'matplotlib.legend.html.template',        
    'matplotlib.lines.html.template',
    'matplotlib.matlab.html.template',
    'matplotlib.mlab.html.template',
    'matplotlib.patches.html.template',
    'matplotlib.table.html.template',    
    'matplotlib.text.html.template',    
    'matplotlib.transforms.html.template',
         )
         

files = [
    'backends.html.template',
    'classdocs.html.template',
    'credits.html.template',
    'faq.html.template',
    'fonts.html.template',
    'goals.html.template',
    'index.html.template',
    'installing.html.template',
    'interactive.html.template',
    'license.html.template',
    'matlab_commands.html.template', 
    'screenshots.html.template',
    'tutorial.html.template',
    'whats_new.html.template', 
         ]
files.extend(docs)
         
         

#print params

keysOrig = {}
for key in locals().keys():
    keysOrig[key] = 1

for inFile in files:
    print '\tConverting', inFile
    fh = file(inFile, 'r')
    s = ''

    while 1:
        line = fh.readline()
        if line.find('@header@')==0:
            break
        s += line
    fileParams = copy.copy(params)
    if len(s)>0: exec(s)
    for key, val in locals().items():
        if not keysOrig.has_key(key):
            fileParams[key] = val

    outFile, ext = os.path.splitext(inFile)
    cop = yaptu.copier(rex, fileParams, rbe, ren, rco, ouf=file(outFile, 'w'))
    lines = ['@header@']
    lines.extend(fh.readlines())
    cop.copy(lines)

