"""
You can use the proper typesetting unicode minus (see
http://en.wikipedia.org/wiki/Plus_sign#Plus_sign) or the ASCII hypen
for minus, which some people prefer.  The matplotlibrc param
axes.unicode_minus controls the default behavior.

The default is to use the unicode minus
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['axes.unicode_minus'] = False
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(10*np.random.randn(100), 10*np.random.randn(100), 'o')
ax.set_title('Using hypen instead of unicode minus')
plt.show()
