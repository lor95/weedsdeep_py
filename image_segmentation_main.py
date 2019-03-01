import os
import cv2 as cv

print("path: ", os.path.dirname(os.path.realpath(__file__)))
print('image path:', end=' ')
img_path = input()
img = cv.imread(img_path)

hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

mask = cv.inRange(hsv, (35, 40, 40), (80, 255, 255)) # valore empirico, l'ideale sarebbe modificare i parametri in base alla tendenza di verde dell'immagine
img = cv.GaussianBlur(mask, (11, 11), 2) # valore empirico, l'ideale sarebbe modificare i parametri in base alla "rumorosità" dell'elemento in input

thr,img = cv.threshold(img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU) # otsu thresholding

#cv.imshow("image", img);cv.waitKey();cv.destroyAllWindows()
cv.imwrite('test.tiff', img) # salva immagine nella cartella corrente