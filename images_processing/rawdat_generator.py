import os
import sys

folder = sys.argv[1]
dest = sys.argv[2]
mode = sys.argv[3] # write/append

files = os.listdir(folder)

if not os.path.exists(dest):
    os.makedirs(dest)

if mode != 'w' and mode != 'a':
    print('\'%s\' mode unknown, standard (write) mode selected.' % mode)
    mode = 'w'

rawdat = open(dest + '/RAW.dat', mode)
for file in files:
    if file.endswith('.jpg'):
        rawdat.write(folder + '/' + file + '\n')

rawdat.close()