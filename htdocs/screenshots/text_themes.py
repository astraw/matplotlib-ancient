from pylab import *

font = {'fontname'   : 'Courier',
        'color'      : 'r',
        'fontweight' : 'bold',
        'fontsize'   : 11}

def f(t):
    s1 = cos(2*pi*t)
    e1 = exp(-t)
    return multiply(s1,e1)

t1 = arange(0.0, 5.0, 0.1)
t2 = arange(0.0, 5.0, 0.02)

lines1 = plot(t1, f(t1), 'ko')
lines2 = plot(t2, f(t2), 'k')
set(lines1, 'markerfacecolor', 'b')
title('Damped exponential decay', font, fontsize=12)
text(2, 0.65, 'cos(2 pi t) exp(-t)', font, color='k')
xlabel('time (s)', font)
ylabel('voltage (mV)', font)

savefig('text_themes_small.png', dpi=60)
savefig('text_themes_large.png', dpi=120)
show()
