from pylab import *

font = {'fontname'   : 'Courier',
        'color'      : 'r',
        'fontweight' : 'bold',
        'fontsize'   : 11}

t = arange(0.0, 5.0, 0.1)

plot(t, cos(2*pi*t)*exp(-t), '-ko', mfc='b')

title('Damped exponential decay', font, fontsize=12)
text(2, 0.65, r'\rm{cos}(2 \pi t) \rm{exp}(-t)', font, color='k')
xlabel('time (s)', font)
ylabel('voltage (mV)', font)

show()
