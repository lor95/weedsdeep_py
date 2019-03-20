# python3 requested

import os
import sys
import cv2 as cv
import numpy as np
import exiftool
import math
import xml.etree.ElementTree as et
from shutil import copyfile
from pyproj import Proj, transform

raw_file_path = sys.argv[1]
tiff_file_path = sys.argv[2]
raster_directory = sys.argv[3]
config_xml_path = sys.argv[4]

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
    config['angle'] = float(param.find('angle').text)
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
    config['area_thr'] = float(param.find('area_thr').text)
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

tiff_file = open(tiff_file_path, 'w')

if not os.path.exists(raster_directory):
    os.makedirs(raster_directory)

for i in range(len(images)): # for each image
    raw_directory = os.path.dirname(images[i])    
    filename = os.path.splitext(os.path.basename(images[i]))[0]  # gets the image file name (without extension)
    
    with exiftool.ExifTool() as e:
        longitude = e.get_tag('EXIF:GPSLongitude', images[i])
        latitude = e.get_tag('EXIF:GPSLatitude', images[i])
    
    if config['crs_transform']:
        longitude, latitude = transform(Proj(init = 'EPSG:4326'), Proj(init = 'EPSG:32633'), longitude, latitude)
  
    # image processing

    img = cv.imread(images[i])  # for loop starts for each img in RAW.dat
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

    img = cv.dilate(img, d_e_kernel, config['iterations']) # dilate n times
    img = cv.erode(img, d_e_kernel, config['iterations']) # erode n times
    
    csv_file = open(raster_directory + '/' + filename + '.csv', 'w')
    header = 'id;area;length;compactness;convexity;solidity;roundness;formfactor;elongation;rect_fit;main_dir;max_axis_len;min_axis_len;num_holes;holesolrat;convex_hull_area;convex_hull_length;outer_contour_area;outer_contour_length\n'
    csv_file.write(header)    
    
    # labeling phase
    
    out = cv.connectedComponentsWithStats(img)
    sizes = out[2][1:, -1]
    area_thr = config['area_thr'] / (config['gsd'] ** 2) # convert area [mq] to area [px]
    for i in range(0, out[0] - 1):
        if sizes[i] >= area_thr: # vegetated area
            _id = i + 1
            img[out[1] == _id] = _id
            temp = img.copy()
            for temp_bg in range(1, out[0]): # set temporarily every feature (except the one considered) as background
                if temp_bg != _id:
                    temp[out[1] == temp_bg] = 0
            contours, hierachy = cv.findContours(temp, cv.RETR_TREE, cv.CHAIN_APPROX_NONE) # get contours of the considered feature

            # evaluate spatial properties

            _convex_hull_area = cv.contourArea(cv.convexHull(contours[0]))
            _convex_hull_length = cv.arcLength(cv.convexHull(contours[0]), True)
            _outer_contour_area = cv.contourArea(contours[0])
            _outer_contour_length = cv.arcLength(contours[0], True)
            _area = _outer_contour_area
            _length = _outer_contour_length
            width, height = cv.boundingRect(contours[0])[2:] # gets bounding rectangle properties, such as width and heigth
            _max_axis_len = max(width, height)
            _min_axis_len = min(width, height)
            _main_dir = cv.fitEllipse(contours[0])[2]
            _numholes = len(contours) - 1
            for cnt in contours[1:]:
                _area -= cv.contourArea(cnt) # subtracts holes' area
                _length += cv.arcLength(cnt, True) # adds holes' perimeter
            _compactness = math.sqrt(4 * _area / math.pi) / _outer_contour_length
            _convexity = _convex_hull_length / _length
            _solidity = _area / _convex_hull_area
            _roundness = (4 / math.pi) * _area / (_max_axis_len ** 2)
            _form_factor = 4 * math.pi * _area / (_length ** 2)
            _elongation = _max_axis_len / _min_axis_len
            _rect_fit = _area / (_max_axis_len * _min_axis_len)
            _holesolrat = _area / _outer_contour_area

            csv_file.write(str(_id) + ';' 
            + str(_area) + ';' 
            + str(_length) + ';' 
            + str(_compactness) + ';'
            + str(_convexity) + ';'
            + str(_solidity) + ';'
            + str(_roundness) + ';' 
            + str(_form_factor) + ';'
            + str(_elongation) + ';'
            + str(_rect_fit) + ';'
            + str(_main_dir) + ';'
            + str(_max_axis_len) + ';'
            + str(_min_axis_len) + ';' 
            + str(_numholes) + ';' 
            + str(_holesolrat) + ';'
            + str(_convex_hull_area) + ';'
            + str(_convex_hull_length) + ';' 
            + str(_outer_contour_area) + ';' 
            + str(_outer_contour_length) + '\n')

        else:
            img[out[1] == i + 1] = 0 # directly adds small elements to background

    csv_file.close()
    
    tiff_file.write(raster_directory + '/' + filename + '.tiff\n')
    cv.imwrite(raster_directory + '/' + filename + '.tiff', img) # save image

    world_file = open(raw_directory + '/' + filename + '.jgw', 'w') # world file    
    world_file.write(str(config['gsd'] * math.cos(config['angle'])) + '\n')
    world_file.write(str(- config['gsd'] * math.sin(config['angle'])) + '\n')
    world_file.write(str(- config['gsd'] * math.sin(config['angle'])) + '\n')
    world_file.write(str(- config['gsd'] * math.cos(config['angle'])) + '\n')
    world_file.write(str(longitude) + '\n')
    world_file.write(str(latitude) + '\n')
    world_file.close()

    copyfile(raw_directory + '/' + filename + '.jgw', raster_directory + '/' + filename + '.tfw')

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
