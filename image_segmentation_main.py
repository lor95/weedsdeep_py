# python3 requested

import os
import sys
import cv2 as cv
import numpy as np
import exiftool
from shutil import copyfile
from pyproj import Proj, transform
import xml.etree.ElementTree as et

raw_file_path = sys.argv[1]
tbands_tiff_path = sys.argv[2] #############################################
tiff_file_path = sys.argv[3]
tbands_raster_directory = sys.argv[4] ########################################
raster_directory = sys.argv[5]
config_xml_path = sys.argv[6]

config = {} # settings array

root = et.parse(config_xml_path).getroot() # contains all the configurations, path should be sent via GUI

# root level
general = root.findall('general')
geo = root.findall('geo_params')
params = root.findall('segmentation_params')
# first level
for conf in general:
    config['show_img'] = int(conf.find('show_img').text)
for param in geo:
    config['crs_transform'] = int(param.find('crs_transform').text)
    config['gsd'] = float(param.find('gsd').text)
    config['rotate_x'] = float(param.find('rotate_x').text)
    config['rotate_y'] = float(param.find('rotate_y').text)
for param in params:
    hsv_mask = param.findall('hsv_mask')
    gauss = param.findall('gaussian_blur')
    dil_er = param.findall('dil_er')
    resize = param.findall('resize')
    labeling = param.findall('labeling')
# second level
for param in hsv_mask:
    hsv_lb = param.findall('lowerb')    
    hsv_ub = param.findall('upperb')
for param in gauss:
    gauss_ker = param.findall('ksize')
    config['sigma'] = int(param.find('sigma').text)
for param in dil_er:
    config['ksize'] = int(param.find('ksize').text)
    config['iterations'] = int(param.find('iterations').text)
for param in resize:
    config['n_times'] = int(param.find('n_times').text)
    config['ratio'] = float(param.find('ratio').text)
    config['interpolation'] = int(param.find('interpolation').text)
for param in labeling:
    config['area_thr'] = int(param.find('area_thr').text)
# third level
for param in hsv_lb:
    config['h_lb'] = int(param.find('h').text)
    config['s_lb'] = int(param.find('s').text)
    config['v_lb'] = int(param.find('v').text)
for param in hsv_ub:
    config['h_ub'] = int(param.find('h').text)
    config['s_ub'] = int(param.find('s').text)
    config['v_ub'] = int(param.find('v').text)
for param in gauss_ker:
    config['gk_x'] = int(param.find('x').text)
    config['gk_y'] = int(param.find('y').text)

if config['interpolation'] == 0:
    config['interpolation'] = cv.INTER_LINEAR
else:
    config['interpolation'] = cv.INTER_NEAREST

images = []

raw_file = open(raw_file_path, 'r')
for line in raw_file:
    images.append(line.strip())
raw_file.close()

mband_tiff_file = open(tbands_tiff_path, 'w') #########################################
tiff_file = open(tiff_file_path, 'w')

if not os.path.exists(tbands_raster_directory): ##################################################
    os.makedirs(tbands_raster_directory) #######################################################

if not os.path.exists(raster_directory):
    os.makedirs(raster_directory)

for i in range(len(images)):    
    filename = os.path.splitext(os.path.basename(images[i]))[0]  # gets the image file name (without extension)
    
    with exiftool.ExifTool() as e:
        longitude = e.get_tag('EXIF:GPSLongitude', images[i])
        latitude = e.get_tag('EXIF:GPSLatitude', images[i])
    
    if config['crs_transform']:
        longitude, latitude = transform(Proj(init = 'EPSG:4326'), Proj(init = 'EPSG:32633'), longitude, latitude)
  
    # image processing

    img = cv.imread(images[i])  # for loop starts for each img in RAW.dat

    cv.imwrite(tbands_raster_directory + '/' + filename + '.tiff', img) ########################################################################

    img = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    img = cv.inRange(img, (config['h_lb'], config['s_lb'], config['v_lb']), (config['h_ub'], config['s_ub'], config['v_ub'])) # mask green, exclude soil

    img = cv.GaussianBlur(img, (config['gk_x'], config['gk_y']), config['sigma'])
    thr, img = cv.threshold(img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)  # otsu thresholding

    d_e_kernel = np.ones((config['ksize'], config['ksize']), np.uint8)
    img = cv.dilate(img, d_e_kernel, config['iterations']) # dilate n times
    img = cv.erode(img, d_e_kernel, config['iterations']) # erode n times

    for i in range(config['n_times']): # resize
        img = cv.resize(img, None, fx = config['ratio'], fy = config['ratio'], interpolation = config['interpolation'])
    for i in range(config['n_times']): # resize
        img = cv.resize(img, None, fx = config['ratio'] ** -1, fy = config['ratio'] ** -1, interpolation = config['interpolation'])

    # labeling phase
    out = cv.connectedComponentsWithStats(img)
    sizes = out[2][1:, -1];
    for i in range(0, out[0] - 1):  
        if sizes[i] >= config['area_thr']:
            img[out[1] == i + 1] = 255 # weed/crop
        else:
            img[out[1] == i + 1] = 0 # add small elements to background

    img = cv.dilate(img, d_e_kernel, config['iterations']) # dilate n times
    img = cv.erode(img, d_e_kernel, config['iterations']) # erode n times
    
    # write data

    mband_tiff_file.write(tbands_raster_directory + '/' + filename + '.tiff\n') #############################################
    tiff_file.write(raster_directory + '/' + filename + '.tiff\n')
    cv.imwrite(raster_directory + '/' + filename + '.tiff', img) # save image
    
    tfw_file = open(tbands_raster_directory + '/' + filename + '.tfw', 'w')
    tfw_file.write(str(config['gsd']) + '\n')
    tfw_file.write(str(config['rotate_y']) + '\n')
    tfw_file.write(str(config['rotate_x']) + '\n')
    tfw_file.write('-' + str(config['gsd']) + '\n')
    tfw_file.write(str(longitude) + '\n')
    tfw_file.write(str(latitude) + '\n')
    tfw_file.close()

    copyfile(tbands_raster_directory + '/' + filename + '.tfw', raster_directory + '/' + filename + '.tfw') #####################################

    # check    
    if config['show_img']:
        winname = filename + ' - Press ESC to quit execution.'
        cv.imshow(winname, img);
        cv.moveWindow(winname, 0, 0)
        key = cv.waitKey();
        if key == 27:
            cv.destroyAllWindows()
            break
        cv.destroyAllWindows()


# end loop
tiff_file.close()
