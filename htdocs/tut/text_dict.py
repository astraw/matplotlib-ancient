from pylab import *
font = {'fontname'   : 'Courier',
        'color'      : 'r',
        'fontweight' : 'bold',
        'fontsize'   : 11}

plot([1,2,3])
title('A title', font, fontsize=12)
text(0.5, 2.5, 'a line', font, color='k')
xlabel('time (s)', font)
ylabel('voltage (mV)', font)
savefig('text_dict')
show()
