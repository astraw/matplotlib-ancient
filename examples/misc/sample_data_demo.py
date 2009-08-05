"""
Grab mpl data from the ~/.matplotlib/sample_data cache if it exists, else
fetch it from svn and cache it
"""
import matplotlib.cbook as cbook
import matplotlib.pyplot as plt
fname = cbook.get_sample_data('lena.png', asfileobj=False)

print 'fname', fname
im = plt.imread(fname)
plt.imshow(im)
plt.show()
