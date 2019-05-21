import os
import argparse

location = os.path.dirname(os.path.abspath(__file__))
parser = argparse.ArgumentParser(description = 'Generates "RAW.dat" file.')
parser.add_argument('dir', action = 'store', type = str,
                    help = 'path to images directory')
parser.add_argument('-fdir', action = 'store', type = str,
                    help = 'directory where "RAW.dat" is saved. Default location is "./"',
                    metavar = '<file_directory>',
                    default = location)
parser.add_argument('-m', action = 'store', type = str,
                    help = 'Writing mode. Default is "w - write"',
                    metavar = '<mode>',
                    default = 'w')
args = parser.parse_args()

files = os.listdir(args.dir)

if not os.path.exists(args.fdir):
    os.makedirs(args.fdir)

if args.m != 'w' and args.m != 'a':
    print('\'%s\' mode unknown, default (write) mode selected.' % args.m)
    args.m = 'w'

rawdat = open(args.fdir + '/RAW.dat', args.m)
for file in files:
    if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png'):
        rawdat.write(args.dir + '/' + file + '\n')

rawdat.close()