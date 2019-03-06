import os
import sys
import cv2 as cv
import numpy as np
import xml.etree.ElementTree as et

config = {} # settings array

root = et.parse('config.xml').getroot() # contains all the configurations, path should be sent via GUI

# root level
paths = root.findall('paths')
params = root.findall('params')
# first level
for path in paths:
    rawdat_ = path.find('rawdat_path').text
    raster_ = path.find('raster_path').text
for param in params:
    hsv_mask = param.find('hsv_mask')
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
for param in labeling:
    config['area_thr'] = int(param.find('area_thr').text)
# third level
for param in hsv_lb:
    config['h_lb'] = int(param.find('h_lb').text)
    config['s_lb'] = int(param.find('s_lb').text)
    config['v_lb'] = int(param.find('v_lb').text)
for param in hsv_ub:
    config['h_ub'] = int(param.find('h_ub').text)
    config['s_ub'] = int(param.find('s_ub').text)
    config['v_ub'] = int(param.find('v_ub').text)
for param in gauss_ker:
    config['gk_x'] = int(param.find('x').text)
    config['gk_y'] = int(param.find('y').text)

img_path = sys.argv[1]  # Gui

# to be removed -> Gui
raw_dat_path = os.path.dirname(os.path.realpath(__file__)) + rawdat_
if not os.path.exists(os.path.dirname(raw_dat_path)):
    os.makedirs(os.path.dirname(raw_dat_path))
raw_dat = open(raw_dat_path, 'w')
raw_dat.write(img_path)
raw_dat.close()
# to be removed -> Gui
tiff_dat_path = os.path.dirname(raw_dat_path) + '/TIFF.dat'
tiff_dat = open(tiff_dat_path, 'w')

filename = os.path.splitext(os.path.basename(img_path))[0]  # gets the image file name (without extension)
raster_directory = os.path.dirname(os.path.realpath(__file__)) + raster_  # Gui (tiff directory)
if not os.path.exists(raster_directory):
    os.makedirs(raster_directory)

# image processing

img = cv.imread(img_path)  # for loop starts for each img in RAW.dat
img = cv.cvtColor(img, cv.COLOR_BGR2HSV)

img = cv.inRange(img, (35,40,40),(80,255,255))
#img = cv.inRange(img, (config['h_lb'], config['s_lb'], config['v_lb']), (config['h_ub'], config['s_ub'], config['v_ub'])) # mask green

img = cv.GaussianBlur(img, (config['gk_x'], config['gk_y']), config['sigma'])
thr, img = cv.threshold(img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)  # otsu thresholding

cv.imshow("thresholding otsu", img);cv.waitKey();cv.destroyAllWindows()

d_e_kernel = np.ones((config['ksize'], config['ksize']), np.uint8)
img = cv.dilate(img, d_e_kernel, config['iterations']) # dilate n times
img = cv.erode(img, d_e_kernel, config['iterations']) # erode n times

cv.imshow("dilation erosion 1", img);cv.waitKey();cv.destroyAllWindows()

for i in range(config['n_times']): # resize
    img = cv.resize(img, None, fx = config['ratio'], fy = config['ratio'], interpolation = cv.INTER_LINEAR) # INTER_NEAREST, INTER_LINEAR
for i in range(config['n_times']): # resize
    img = cv.resize(img, None, fx = config['ratio'] ** -1, fy = config['ratio'] ** -1, interpolation = cv.INTER_LINEAR) # INTER_NEAREST, INTER_LINEAR

cv.imshow("resized", img);cv.waitKey();cv.destroyAllWindows()

# labeling phase
out = cv.connectedComponentsWithStats(img)
sizes = out[2][1:, -1];
for i in range(0, out[0] - 1):  
    if sizes[i] >= config['area_thr']:
        img[out[1] == i + 1] = 255 # label
    else:
        img[out[1] == i + 1] = 0 # background

cv.imshow("labeled", img);cv.waitKey();cv.destroyAllWindows()

img = cv.dilate(img, d_e_kernel, config['iterations']) # dilate n times
img = cv.erode(img, d_e_kernel, config['iterations']) # erode n times

cv.imshow("dilation erosion 2", img);cv.waitKey();cv.destroyAllWindows()

# write data
tiff_dat.write(raster_directory + '/' + filename +'.tiff')
cv.imwrite(raster_directory + '/' + filename +'.tiff', img) # salva immagine

tiff_dat.close()
