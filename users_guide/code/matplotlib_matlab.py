# python                               % matlab
from pylab import *        % no import necessary

dt = 0.01                              dt = 0.01;
t = arange(0,10,dt)                    t = [0:dt:10];
nse = randn(len(t))                    nse = randn(size(t));
r = exp(-t/0.05)                       r = exp(-t/0.05);

cnse = conv(nse, r)*dt                 cnse = conv(nse, r)*dt;
cnse = cnse[:len(t)]                   cnse = cnse(1:length(t));
s = 0.1*sin(2*pi*t) + cnse             s = 0.1*sin(2*pi*t) + cnse;

subplot(211)                           subplot(211)
plot(t,s)                              plot(t,s)
subplot(212)                           subplot(212)
psd(s, 512, 1/dt)                      psd(s, 512, 1/dt)
