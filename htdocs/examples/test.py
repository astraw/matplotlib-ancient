from matplotlib.matlab import *
figure(figsize=(8,8))
ax = axes([0.1, 0.1, 0.8, 0.8])
d=arange(201)*pi/100
plot(10+cos(d),sin(d))
axis('equal')
show()

