import os
import sys
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img

raw_file_path = sys.argv[1]
dest_directory = sys.argv[2]

images = []

raw_file = open(raw_file_path, 'r')
for line in raw_file:
    images.append(line.strip())
raw_file.close()

if not os.path.exists(dest_directory):
    os.makedirs(dest_directory)

datagen = ImageDataGenerator(
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest')

for image in images:
        
    img = load_img(image)  # this is a PIL image
    x = img_to_array(img)  # this is a Numpy array with shape (3, 150, 150)
    # resize here
    x = x.reshape((1,) + x.shape)  # this is a Numpy array with shape (1, 3, 150, 150)

    # the .flow() command below generates batches of randomly transformed images
    # and saves the results to the `preview/` directory
    i = 0
    for batch in datagen.flow(x,
                          batch_size = 1,
                          save_to_dir = dest_directory,
                          save_prefix = 'plant',
                          save_format = 'jpeg'):
        i += 1
        if i >= 5:
            break  # otherwise the generator would loop indefinitely