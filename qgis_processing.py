# Only works with QGIS >= 3 

import os
import processing
import qgis.utils
#from qgis.core import *
from PyQt5 import QtWidgets
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry

# Load input dialog
qid = QtWidgets.QInputDialog()
title = "qgis_processing"
label = "Enter config-qgis.ini path:"
mode = QtWidgets.QLineEdit.Normal
path, res = QtWidgets.QInputDialog.getText(qid, title, label, mode) # path -> path to config-qgis.ini

# initialization

config = []  # contains all the configurations
config_qgis_ini = open(path, 'r')  # Gui
for line in config_qgis_ini:
    if not line.startswith('#'):
        config.append(line.strip().split(': ')[1])  # gets all characters after ': ' from all lines
config_qgis_ini.close()

raw_dat_path = os.path.dirname(path) + config[0] # path to RAW.dat
tiff_dat_path = os.path.dirname(path) + config[1] # path to TIFF.dat
shapefile_directory = os.path.dirname(path) + config[2]
if not os.path.exists(shapefile_directory):
    os.makedirs(shapefile_directory)
raws = []
tiffs = []
file_raw = open(raw_dat_path, 'r')
for line in file_raw:
	raws.append(line.strip())
file_raw.close()
file_tiff = open(tiff_dat_path, 'r')
for line in file_tiff:
	tiffs.append(line.strip())
file_tiff.close()
# Load Raster
filename = os.path.splitext(os.path.basename(tiffs[0]))[0] # gets the first .tiff file name (without extension)

qgis.utils.iface.addRasterLayer(tiffs[0], filename)

layer = qgis.utils.iface.activeLayer()
entries = []

# Define band1
band = QgsRasterCalculatorEntry()
band.ref = filename + '@1'
band.raster = layer
band.bandNumber = 1
entries.append(band)

# Raster calculation process
calc = QgsRasterCalculator(band.ref, tiffs[0], "GTiff", layer.extent(), layer.width(), layer.height(), entries)
calc.processCalculation() # creates a Raster GDAL-compatible (editable), overwrites old tiff file

processing.run(r"gdal:polygonize",
{'INPUT': tiffs[0],
	'BAND': 1,
	'FIELD': 'VEGETATED',
	'EIGHT_CONNECTEDNESS': 1,
	'OUTPUT': shapefile_directory + "/" + filename + ".shp"})
qgis.utils.iface.addRasterLayer(raws[0], filename)
qgis.utils.iface.addVectorLayer(shapefile_directory + "/" + filename + ".shp", 'SHP', 'ogr')
