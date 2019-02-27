import os
import cv2 as cv

print("path: ", os.path.dirname(os.path.realpath(__file__)))
print('image path:', end=' ')
img_path = input()
img = cv.imread(img_path, 0)

img = cv.GaussianBlur(img, (11, 11), 2) # valore empirico, l'ideale sarebbe modificare i parametri in base alla "rumorosità" dell'elemento in input
thr,img = cv.threshold(img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU) # otsu thresholding
cv.imwrite('test.tiff', img) # salva immagine nella cartella corrente