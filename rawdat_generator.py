import os
import sys

folder = sys.argv[1]
dest = sys.argv[2]

files = os.listdir(folder)

if not os.path.exists(dest):
    os.makedirs(dest)

rawdat = open(dest + '/RAW.dat', 'w')
for file in files:
    rawdat.write(folder + '/' + file + '\n')

rawdat.close