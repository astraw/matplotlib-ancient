from matplotlib.matlab import *

dt = 0.01
t = arange(dt, 20.0, dt)


subplot(211)
semilogx(t, sin(2*pi*t))
ylabel('semilog')
set(gca(), 'xlim', [0,20])
set(gca(), 'xticklabels', [])
grid('on')

subplot(212)
loglog(t, exp(-t/10.0))
grid('on')
set(gca(), 'xlim', [0,20])
xlabel('time (s)')
ylabel('loglog')

savefig('log_shot_small', dpi=60)
savefig('log_shot_large', dpi=120)
show()

