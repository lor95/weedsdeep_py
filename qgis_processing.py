# Only works with QGIS >= 3 

import os
import processing
import qgis.utils
from qgis.core import *
from PyQt5 import QtWidgets # QGIS >= 3
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
#from osgeo import gdal, ogr#, osr

# Load input dialog
qid = QtWidgets.QInputDialog()
title = "qgis_processing"
label = "Enter TIFF path:"
mode = QtWidgets.QLineEdit.Normal
path, res = QtWidgets.QInputDialog.getText(qid, title, label, mode) # path = path to tiff

# Load Raster

filename = os.path.splitext(os.path.basename(path))[0] # gets the .tiff file name (without extension)

qgis.utils.iface.addRasterLayer(path, filename) ###############

#####################################################################################################

layer = qgis.utils.iface.activeLayer()
entries = []

# Define band1
band = QgsRasterCalculatorEntry()
band.ref = filename + '@1'
band.raster = layer
band.bandNumber = 1
entries.append(band)

# Raster calculation process
calc = QgsRasterCalculator(band.ref, path, "GTiff", layer.extent(), layer.width(), layer.height(), entries)# + '/255', path, "GTiff", layer.extent(), layer.width(), layer.height(), entries)
calc.processCalculation() # creates a Raster GDAL-compatible (editable), overwrites old tiff file

###################################################################################################

processing.run(r"gdal:polygonize",
{'INPUT': path,
	'BAND': 1,
	'FIELD': 'VEGETATED',
	'EIGHT_CONNECTEDNESS': 1,
	'OUTPUT': os.path.dirname(path) + "/" + filename + ".shp"})

qgis.utils.iface.addVectorLayer(os.path.dirname(path) + "/" + filename + ".shp", 'SHP', 'ogr')

############################################################################

## shell command: python3 -m gdal_polygonize path\to\test.tiff path\to\OUTPUT.shp -b 1 -f "ESRI Shapefile" OUTPUT DN -mask path\to\test.tiff