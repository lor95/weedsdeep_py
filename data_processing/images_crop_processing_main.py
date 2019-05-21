import os
import argparse
import random
import cv2 as cv

location = os.path.dirname(os.path.abspath(__file__)) + '/default'
parser = argparse.ArgumentParser(description = 'Randomly crops images to enlarge dataset.')
parser.add_argument('img', action = 'store', type = str,
                    help = 'file that contains paths of the images to be cropped')
parser.add_argument('lbl', action = 'store', type = str,
                    help = 'file that contains paths of the labels to be cropped')
parser.add_argument('-idir', action = 'store', type = str,
                    help = 'directory where the cropped images are saved. Default location is "./default/image"',
                    metavar = '<images_directory>',
                    default = location + '/images/image')
parser.add_argument('-ldir', action = 'store', type = str,
                    help = 'directory where the cropped labeled images are saved. Default location is "./default/label"',
                    metavar = '<labels_directory>',
                    default = location + '/images/label')
parser.add_argument('-width', action = 'store', type = int,
                    help = 'width of the cropped image. Default is "512"',
                    metavar = '<width>',
                    default = 512)
parser.add_argument('-height', action = 'store', type = int,
                    help = 'height of the cropped image. Default is "512"',
                    metavar = '<height>',
                    default = 512)
parser.add_argument('-n', action = 'store', type = int,
                    help = 'number of newly generated images per image. Default is "10"',
                    metavar = '<imgs_per_img>',
                    default = 10)
parser.add_argument('-f', action = 'store', type = str,
                    help = 'format in which images are saved. Default is ".jpg"',
                    metavar = '<save_format>',
                    default = 'jpg')
args = parser.parse_args()

images = []
labels = []

raw_file = open(args.img, 'r')
for line in raw_file:
    images.append(line.strip())
raw_file.close()
tiff_file = open(args.lbl, 'r')
for line in tiff_file:
    labels.append(line.strip())
tiff_file.close()

filename = 0

if not os.path.exists(args.idir):
    os.makedirs(args.idir)
if not os.path.exists(args.ldir):
    os.makedirs(args.ldir)

for i in range(len(images)):
    image = cv.imread(images[i])
    label = cv.imread(labels[i], 0)
    h, w = image.shape[:2]
    trial = 0
    while trial < args.n:
        tl_x = random.randrange(0, w - args.width)
        tl_y = random.randrange(0, h - args.height)
        roi_lbl = label[tl_y:(tl_y + args.height), tl_x:(tl_x + args.width)]
        out = cv.connectedComponentsWithStats(roi_lbl)
        sizes = out[2][1:, -1]
        t_area = 0
        for i in range(0, out[0] - 1):
            roi_lbl[out[1] == i + 1] = 255
            t_area += sizes[i]
        if float(t_area / (args.width * args.height)) >= 0.08:
            roi_img = image[tl_y:(tl_y + args.height), tl_x:(tl_x + args.width)]
            cv.imwrite(args.idir + '/' + str(filename) + '.' + args.f, roi_img) # save image
            cv.imwrite(args.ldir + '/' + str(filename) + '.' + args.f, roi_lbl) # save label
            trial += 1
            filename += 1

