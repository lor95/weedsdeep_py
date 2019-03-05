import os
import cv2 as cv

print("path: ", os.path.dirname(os.path.realpath(__file__)))
print('image path:', end=' ')
img_path = input() # argv

config = [] # contains all the configurations
config_ini = open('config.ini', 'r') # argv
for line in config_ini:
    if not line.startswith('#'):
        config.append(line.strip().split(': ')[1]) # gets all characters after ': ' from all lines
config_ini.close()
		
# to be removed
img_dat_path = os.path.dirname(os.path.realpath(__file__)) + config[0]
if not os.path.exists(os.path.dirname(img_dat_path)):
    os.makedirs(os.path.dirname(img_dat_path))
img_dat  = open(img_dat_path, 'w')
img_dat.write(img_path)

filename = os.path.splitext(os.path.basename(img_path))[0] # gets the image file name (without extension)
raster_directory = os.path.dirname(os.path.realpath(__file__)) + config[1] # tiff directory must be defined in config.ini or GUI
if not os.path.exists(raster_directory):
    os.makedirs(raster_directory)

# image processing

img = cv.imread(img_path) # argv
hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

green_lb = config[2].split(';')[0]
green_ub = config[2].split(';')[1]
mask = cv.inRange(hsv, (int(green_lb.split(' ')[0]), int(green_lb.split(' ')[1]), int(green_lb.split(' ')[2])), 
                  (int(green_ub.split(' ')[0]), int(green_ub.split(' ')[1]), int(green_ub.split(' ')[2])))

ksize = config[3].split(';')[0]
sigma = config[3].split(';')[1]
img = cv.GaussianBlur(mask, (int(ksize.split(' ')[0]), int(ksize.split(' ')[1])), int(sigma))
thr,img = cv.threshold(img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU) # otsu thresholding

#cv.imshow("image", img);cv.waitKey();cv.destroyAllWindows()

cv.imwrite(raster_directory + '/' + filename +'.tiff', img) # salva immagine nella cartella corrente