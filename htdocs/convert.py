import yaptu
import re, os, sys, copy
from StringIO import StringIO

from hthelpers import modules
rex=re.compile('@([^@]+)@')
rbe=re.compile('\s*\+')
ren=re.compile('\s*-')
rco=re.compile('\s*= ')


class NewsBox:
    def __init__(self, body):
        self.body = body

    def format_header(self):
        return """
    <tr><td  bgcolor="red" align="left">
        <font class="tableheading">
                <b>News flash</b>
        </font>
    </td></tr>
    """ % self.header
            

    def __repr__(self):
        s =  '<table width=100% border=1 cellpadding=1 ' +\
               'cellspacing=1>\n'
        s += self.format_header()
        s += '<tr><td valign="top" bgcolor=#efefef>\n'
        s += '<font color="red">%s</font>'%self.body
        s += '</td></tr>\n'
        s += '</table>\n'
        return s

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

class FormatGoals:
    """Reads simple text file of goals and formats as html table"""
    
    def __init__(self, filename):
        self.table = []
        f = open(filename)
        self.lines = f.readlines()
        self.nline = 0
        self.format_table()
    def nextline(self):
        self.nline += 1
    def getline(self):
        if self.nline >= len(self.lines):
            return None
        else:
            return self.lines[self.nline].strip()
            
    def format_table(self):
        while 1:
            line = self.getline()
            if line is None: # all done!
                return
            if isBlank(line) or isComment(line):  # comment or empty, ignore
                pass
            elif onlyContains(line, '='): # Toplevel table heading section
                self.nextline()
                self.table.append("<tr><td colspan=3 bgcolor=#c0c0c0><b>")
                self.table.append(self.getline())
                self.table.append("</b></td></tr>")
            elif onlyContains(line, '+'): # Second level table heading section
                self.nextline()
                self.table.append("<tr><td colspan=3 bgcolor=#dddddd><b>")
                self.table.append(self.getline())
                self.table.append("</b></td></tr>")
                
            elif onlyContains(line, '*'): # Regular table entry
                # suck up any intervening blank lines
                self.nextline()
                while isBlank(self.getline()):
                    self.nextline()
                self.parse_entry()
                continue
            else:
                print "WARNING: goals text file is malformed at or around line", \
                    self.nline
            self.nextline()                      
                                  
    def parse_entry(self):
        """Deal with the different components of a normal goal row"""
        ncol = 0
        cols = [[], [], []]
        while 1:
            line = self.getline()
            if line is None or isNewEntry(line):   # End of file or new entry
                self.addrow(cols)                  # only way out of this loop
                return
            if isComment(line):
                pass
            elif not isBlank(line):
                cols[ncol].append(line)
                self.nextline()
            else: # suck up any following blank lines
                while isBlank(line):
                    self.nextline()
                    line = self.getline()
                    if line is None:
                        break
                ncol += 1
                if ncol > 2:
                    ncol = 2
               
    def addrow(self, cols):
        """Format the entry for a row"""
        ncol = 0
        self.table.append("<tr>")
        for col in cols:
            self.table.append("<td>")
            for line in col:
                self.table.append(line)
            if not len(col):
                self.table.append("&nbsp;")
                #self.table.append("<font color=#ffffff>.</font>") # need something in cell to format well
            self.table.append("</td>")
            ncol += 1
        self.table.append("</tr>")      
                    
    def __repr__(self):
        return "\n".join(self.table)

# helper functions for FormatGoals
def onlyContains(line, char):
    """Does line only contain one or more instances of given character?
    
    (aside from leading or trailing whitespace)"""

    tline = line.strip()
    if len(tline) and len(tline)*char == tline:
        return 1
    else:
        return 0

def isComment(line):
    return line.strip() and (line.strip()[0] == '#')
    
def isBlank(line):  
    return not line.strip()
    
            
def isNewEntry(line):
    if (onlyContains(line, '=') or 
        onlyContains(line, '+') or 
        onlyContains(line, '*')):
        return 1
    else:
        return 0

news = NewsBox("""\
matlab interface now named pylab.  See <a href=matlab_to_pylab.py>matlab_to_pylab.py</a> for conversion details</a>
""")

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
    ('pylab&nbsp;interface', 'pylab_commands.html'),
    ('Class&nbsp;library', 'classdocs.html'),
    ('Backends', 'backends.html'),
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

docs = [modname + '.html.template' for modname in modules]
         

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
    'pylab_commands.html.template', 
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

