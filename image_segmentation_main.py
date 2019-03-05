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
img_dat_path = os.path.dirname(os.path.realpath(__file__)) + config[0]
if not os.path.exists(os.path.dirname(img_dat_path)):
    os.makedirs(os.path.dirname(img_dat_path))
img_dat = open(img_dat_path, 'w')
img_dat.write(img_path)
img_dat.close()

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
cv.imshow("image", img);cv.waitKey();cv.destroyAllWindows()

d_e_kernel = np.ones((int(config[4].split(';')[0]),int(config[4].split(';')[0])), np.uint8)
img = cv.dilate(img, d_e_kernel)#, int(config[4].split(';')[1])) # dilate n times
img = cv.erode(img, d_e_kernel)#, int(config[4].split(';')[1])) # erode n times
cv.imshow("image", img);cv.waitKey();cv.destroyAllWindows()

for i in range(int(config[5])): # resize
    img = cv.resize(img, None, fx = float(config[6]), fy = float(config[6]), 
                    interpolation = cv.INTER_NEAREST)
for i in range(int(config[5])): # resize
    img = cv.resize(img, None, fx = float(config[6]) ** -1, fy = float(config[6]) ** -1, 
                    interpolation = cv.INTER_NEAREST)

cv.imshow("image", img);cv.waitKey();cv.destroyAllWindows()

out = cv.connectedComponentsWithStats(img)
#print(out[0])
#for label in range(1,out[0]):
#    mask = np.array(out[1], dtype=np.uint8)
#    mask[out[1] == label] = 255
    
#for i in range(1, out[0]):
#    lblareas = out[2][0:, cv.CC_STAT_AREA]
#    print(lblareas)
#    imax = max(enumerate(lblareas), key=(lambda x: x[1]))[0] + 1
#    cv.rectangle(img, (int(out[2][imax, cv.CC_STAT_LEFT]),int(out[2][imax, cv.CC_STAT_TOP])), (int(out[2][imax, cv.CC_STAT_LEFT])+int(out[2][imax, cv.CC_STAT_WIDTH]), int(out[2][imax, cv.CC_STAT_TOP])+int(out[2][imax, cv.CC_STAT_HEIGHT])), (255,0,0), 2)
#cv.imshow("image", img);cv.waitKey();cv.destroyAllWindows()

img = cv.dilate(img, d_e_kernel, int(config[4].split(';')[1])) # dilate
img = cv.erode(img, d_e_kernel, int(config[4].split(';')[1])) # erode
cv.imshow("image", img);cv.waitKey();cv.destroyAllWindows()

cv.imwrite(raster_directory + '/' + filename +'.tiff', img) # salva immagine nella cartella corrente
