# read in the cvs file family.dat

# open the file for reading
fh = file('../data/family.csv', 'r')

# slurp the header, splitting on the comma
headers = fh.readline().split(',')

# now loop over the remaining lines in the file and parse them
for line in fh:
    # remove any leading or trailing white space
    line = line.strip()
    # split the line on the comma into separate variables
    first, last, age, weight, height, dob = line.split(',')
    # convert some of these strings to floats
    age, weight, height = [float(val) for val in (age, weight, height)]
    print first, last, age, weight, height, dob


results = []
for line in fh:
    # process the line as above to get the variables
    results.append( (first, last, age, weight, height, dob) )
