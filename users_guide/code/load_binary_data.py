# load the data as a string
s = file('../data/binary_data.dat', 'rb').read()

# convert to 1D numerix array of type Float
X = fromstring(s, Float)

# reshape to numSamples rows by 2 columns
X.shape = len(X)/2, 2
t = X[:,0]  # the first column
s = X[:,1]  # the second row
plot(t, s, 'o')


