import os
import cv2 as cv
import numpy as np

print("path: ", os.path.dirname(os.path.realpath(__file__)))
print('image path:', end=' ')
img_path = input()  # Gui

config = []  # contains all the configurations
config_ini = open('config.ini', 'r')  # Gui
for line in config_ini:
    if not line.startswith('#'):
        config.append(line.strip().split(': ')[1])  # gets all characters after ': ' from all lines
config_ini.close()

# to be removed -> Gui
raw_dat_path = os.path.dirname(os.path.realpath(__file__)) + config[0]
if not os.path.exists(os.path.dirname(raw_dat_path)):
    os.makedirs(os.path.dirname(raw_dat_path))
raw_dat = open(raw_dat_path, 'w')
raw_dat.write(img_path)
raw_dat.close()
# to be removed -> Gui
tiff_dat_path = os.path.dirname(raw_dat_path) + '/TIFF.dat'

filename = os.path.splitext(os.path.basename(img_path))[0]  # gets the image file name (without extension)
raster_directory = os.path.dirname(os.path.realpath(__file__)) + config[1]  # Gui (tiff directory)
if not os.path.exists(raster_directory):
    os.makedirs(raster_directory)

# image processing

img = cv.imread(img_path)  # for loop starts for each img in RAW.dat
img = cv.cvtColor(img, cv.COLOR_BGR2HSV)

green_lb = config[2].split(';')[0]
green_ub = config[2].split(';')[1]
img = cv.inRange(img, (int(green_lb.split(' ')[0]), int(green_lb.split(' ')[1]), int(green_lb.split(' ')[2])),
                  (int(green_ub.split(' ')[0]), int(green_ub.split(' ')[1]), int(green_ub.split(' ')[2]))) # mask green

ksize = config[3].split(';')[0]
sigma = config[3].split(';')[1]
img = cv.GaussianBlur(img, (int(ksize.split(' ')[0]), int(ksize.split(' ')[1])), int(sigma)) 
thr, img = cv.threshold(img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)  # otsu thresholding
cv.imshow("thresholding otsu", img);cv.waitKey();cv.destroyAllWindows()

d_e_kernel = np.ones((int(config[4].split(';')[0]),int(config[4].split(';')[0])), np.uint8)
img = cv.dilate(img, d_e_kernel, int(config[4].split(';')[1])) # dilate n times
img = cv.erode(img, d_e_kernel, int(config[4].split(';')[1])) # erode n times
cv.imshow("dilation erosion 1", img);cv.waitKey();cv.destroyAllWindows()

for i in range(int(config[5])): # resize
    img = cv.resize(img, None, fx = float(config[6]), fy = float(config[6]), 
                    interpolation = cv.INTER_LINEAR) # INTER_NEAREST, INTER_LINEAR
for i in range(int(config[5])): # resize
    img = cv.resize(img, None, fx = float(config[6]) ** -1, fy = float(config[6]) ** -1, 
                    interpolation = cv.INTER_LINEAR) # INTER_NEAREST, INTER_LINEAR
cv.imshow("resized", img);cv.waitKey();cv.destroyAllWindows()

# labeling phase
out = cv.connectedComponentsWithStats(img)
sizes = out[2][1:, -1];
min_size = int(config[7])
for i in range(0, out[0] - 1):  
    if sizes[i] >= min_size:
        img[out[1] == i + 1] = 255
    else:
        img[out[1] == i + 1] = 0
cv.imshow("labeled", img);cv.waitKey();cv.destroyAllWindows()

img = cv.dilate(img, d_e_kernel, int(config[4].split(';')[1])) # dilate
img = cv.erode(img, d_e_kernel, int(config[4].split(';')[1])) # erode
cv.imshow("dilation erosion 2", img);cv.waitKey();cv.destroyAllWindows()

tiff_dat = open(tiff_dat_path, 'w')
tiff_dat.write(raster_directory + '/' + filename +'.tiff')
tiff_dat.close()
cv.imwrite(raster_directory + '/' + filename +'.tiff', img) # salva immagine nella cartella corrente
