from pylab import *

dt = 0.01
t = arange(dt, 20.0, dt)

subplot(211)
semilogx(t, sin(2*pi*t))
ylabel('semilog')
xticks([])
setp(gca(), 'xticklabels', [])
grid(True)

subplot(212)
loglog(t, 20*exp(-t/10.0), basey=4)
grid(True)
gca().xaxis.grid(True, which='minor')  # minor grid on too
xlabel('time (s)')
ylabel('loglog')
show()

