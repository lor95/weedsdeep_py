import os
import argparse
import xml.etree.ElementTree as et
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img

location = os.path.dirname(os.path.abspath(__file__)) + '/default'
parser = argparse.ArgumentParser(description = 'Randomly transforms images to enlarge dataset.')
parser.add_argument('config', action = 'store', type = str,
                    help = 'path to config.xml file')
parser.add_argument('list', action = 'store', type = str,
                    help = 'file that contains paths of the images to be transformed')
parser.add_argument('-n', action = 'store', type = int,
                    help = 'number of random transformations per image. Default is "3"',
                    metavar = '<n_transform>',
                    default = 3)
parser.add_argument('-rdir', action = 'store', type = str,
                    help = 'directory where the images are saved. Default location is "./default/images"',
                    metavar = '<results_directory>',
                    default = location + '/images')
parser.add_argument('-p', action = 'store', type = str,
                    help = 'adds a prefix to newly generated images. Default is "image"',
                    metavar = '<save_prefix>',
                    default = 'image')
parser.add_argument('-f', action = 'store', type = str,
                    help = 'format in which images are saved. Default is ".jpg"',
                    metavar = '<save_format>',
                    default = 'jpg')
args = parser.parse_args()

config = {} # settings array
data = {} # data array

root = et.parse(args.config).getroot() # contains all the configurations

# root level
augmentation = root.findall('augmentation_params')
# first level
for param in augmentation:
    batch = param.findall('batch')
    values = param.findall('values')
# second level
for param in batch:
    config['rotation'] = int(param.find('rotation').text)
    config['width_shift'] = int(param.find('width_shift').text)
    config['height_shift'] = int(param.find('height_shift').text)
    config['channel_shift'] = int(param.find('channel_shift').text)
    config['shear'] = int(param.find('shear').text)
    config['zoom'] = int(param.find('zoom').text)
    config['horizontal_flip'] = int(param.find('horizontal_flip').text)
    config['vertical_flip'] = int(param.find('vertical_flip').text)
for param in values:
    data['rotation'] = int(param.find('rotation_range').text)
    data['width_shift'] = float(param.find('width_shift_range').text)
    data['height_shift'] = float(param.find('height_shift_range').text)
    data['channel_shift'] = float(param.find('channel_shift_range').text)
    data['shear'] = float(param.find('shear_range').text)
    data['zoom'] = float(param.find('zoom_range').text)

for elem in config:
    if config[elem] == 0:
        data[elem] = 0

images = []

raw_file = open(args.list, 'r')
for line in raw_file:
    images.append(line.strip())
raw_file.close()

if not os.path.exists(args.rdir):
    os.makedirs(args.rdir)

datagen = ImageDataGenerator(
        rotation_range = data['rotation'],
        width_shift_range = data['width_shift'],
        height_shift_range = data['height_shift'],
        shear_range = data['shear'],
        zoom_range = data['zoom'],
        horizontal_flip = config['horizontal_flip'],
        vertical_flip = config['vertical_flip'],
        fill_mode = 'constant')

# generate images
for image in images:
    img = load_img(image)
    x = img_to_array(img)
    x = x.reshape((1,) + x.shape)

    i = 0
    for batch in datagen.flow(x,
                          batch_size = 1,
                          save_to_dir = args.rdir,
                          save_prefix = args.p,
                          save_format = args.f):
        i += 1
        if i >= args.n:
            break  # otherwise the generator would loop indefinitely