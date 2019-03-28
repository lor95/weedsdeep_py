import os
import sys
import xml.etree.ElementTree as et
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img

raw_file_path = sys.argv[1]
dest_directory = sys.argv[2]
config_xml_path = sys.argv[3]

config = {} # settings array
data = {} # data array

root = et.parse(config_xml_path).getroot() # contains all the configurations

# root level
augmentation = root.findall('augmentation_params')
# first level
for param in augmentation:
    batch = param.findall('batch')
    values = param.findall('values')
# second level
for param in batch:
    config['n_transform'] = int(param.find('n_transform').text)
    config['rotation'] = int(param.find('rotation').text)
    config['width_shift'] = int(param.find('width_shift').text)
    config['height_shift'] = int(param.find('height_shift').text)
    config['shear'] = int(param.find('shear').text)
    config['zoom'] = int(param.find('zoom').text)
    config['horizontal_flip'] = int(param.find('horizontal_flip').text)
for param in values:
    data['rotation'] = int(param.find('rotation_range').text)
    data['width_shift'] = float(param.find('width_shift_range').text)
    data['height_shift'] = float(param.find('height_shift_range').text)
    data['shear'] = float(param.find('shear_range').text)
    data['zoom'] = float(param.find('zoom_range').text)

for elem in config:
    if config[elem] == 0:
        data[elem] = 0

images = []

raw_file = open(raw_file_path, 'r')
for line in raw_file:
    images.append(line.strip())
raw_file.close()

if not os.path.exists(dest_directory):
    os.makedirs(dest_directory)

datagen = ImageDataGenerator(
        rotation_range = data['rotation'],
        width_shift_range = data['width_shift'],
        height_shift_range = data['height_shift'],
        shear_range = data['shear'],
        zoom_range = data['zoom'],
        horizontal_flip = config['horizontal_flip'],
        fill_mode = 'constant')

for image in images:        
    img = load_img(image)  # this is a PIL image
    x = img_to_array(img)  # this is a Numpy array with shape (3, 150, 150)
    # resize here
    x = x.reshape((1,) + x.shape)  # this is a Numpy array with shape (1, 3, 150, 150)

    i = 0
    for batch in datagen.flow(x,
                          batch_size = 1,
                          save_to_dir = dest_directory,
                          save_prefix = 'plant',
                          save_format = 'jpg'):
        i += 1
        if i >= config['n_transform']:
            break  # otherwise the generator would loop indefinitely