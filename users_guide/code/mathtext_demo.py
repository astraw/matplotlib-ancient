from pylab import *
# use a custom axes to provide room for the large labels used below
ax = axes([.2, .2, .7, .7], axisbg='y')

# generate some random symbols to plot
x = rand(40)
plot(x[:-1], x[1:], 'go', markeredgecolor='k', markersize=14)

# this is just a made up equation that has nothing to do with the
# plot!
s = r'$\cal{R}\prod_{i=\alpha}^\infty a_i\rm{sin}(2 \pi f x_i)$'
text(0.2, 1.2, s, fontsize=20)
axis([-0.2, 1.2, -0.2, 1.8]) 

# subscripts, superscripts and groups with {} are supported
xlabel('$\Delta_i^j$', fontsize='x-large')
ylabel('$\Delta_{i+1}^j$', fontsize='x-large')

savefig('../figures/mathtext_demo.eps')
savefig('../figures/mathtext_demo.png')
show()
