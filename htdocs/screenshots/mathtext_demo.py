from matplotlib.matlab import *

plot([1,2,3])
xlabel(r'$\Delta_i$')
ylabel(r'$\Delta_{i+1}$', # no rotation yet for mathtext
       verticalalignment='center',
       horizontalalignment='right',
       rotation='horizontal')
tex = r'$\cal{R}\prod_{i=\alpha_{i+1}}^\infty a_i\rm{sin}(2 \pi f x_i)$'
text(0.4, 2.4, tex, fontsize=20)
title(r'$\Delta_i \/ \rm{versus} \/ \Delta_{i+1}$', fontsize=15)
savefig('mathtext_demo', dpi=100)
show()
