from model import *
import os
import argparse
from matplotlib import pyplot as plt
from tensorflow.python.keras.preprocessing.image import img_to_array, load_img

def plotbn(img, title):
    plt.figure()
    path = 'C:/Users/Lorenzo/Desktop/predict_images/'
    plt.title(title)
    plt.imshow(img, cmap=plt.cm.gray)
    plt.savefig(path + str(sys.argv[1]) + '_predict.png')

location = os.path.dirname(os.path.abspath(__file__)) + '/default'
parser = argparse.ArgumentParser(description = 'Segmentation Prediction.')
parser.add_argument('list', action = 'store', type = str,
                    help = 'file that contains paths of the images to be processed')
parser.add_argument('-rdir', action = 'store', type = str,
                    help = 'directory where processed images are saved. Default location is "./default/images"',
                    metavar = '<rasters_directory>',
                    default = location + '/images/')
args = parser.parse_args()

if not os.path.exists(args.rdir):
    os.makedirs(args.rdir)

model = unet("myUnet3.hdf5")
images = []

raw_file = open(args.list, 'r')
for line in raw_file:
    images.append(line.strip())
raw_file.close()

for i in range(len(images)):
    img = load_img(images[i])
    img = img_to_array(img)
    img = img.reshape((1,) + img.shape)
    img = model.predict(img/127.5 - 1, batch_size=1, verbose=1)
    plt.figure()
    plt.title('prediction')
    plt.imshow(img[0,:,:,0], cmap=plt.cm.gray)
    plt.savefig(args.rdir + os.path.splitext(os.path.basename(images[i]))[0] + '_predict.png')

raw_file.close()