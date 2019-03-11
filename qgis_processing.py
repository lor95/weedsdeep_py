# REQUIRED QGIS >= 3

import os
import processing
import qgis.utils
from qgis.core import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import QVariant
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry

# Load input dialog -> to be removed
qid = QtWidgets.QInputDialog()
title = "qgis_processing"
label = "Enter config-qgis.ini path:"
mode = QtWidgets.QLineEdit.Normal
path, res = QtWidgets.QInputDialog.getText(qid, title, label, mode) # path -> path to config-qgis.ini

# initialization

crs = QgsCoordinateReferenceSystem("EPSG:4326")
QgsProject.instance().setCrs(crs) # standard crs (does not work!)

config = []  # contains all the configurations
config_qgis_ini = open(path, 'r')  # Gui
for line in config_qgis_ini:
    if not line.startswith('#'):
        config.append(line.strip().split(': ')[1])  # gets all characters after ': ' from all lines
config_qgis_ini.close()

raw_dat_path = os.path.dirname(path) + config[0] # path to RAW.dat
tiff_dat_path = os.path.dirname(path) + config[1] # path to TIFF.dat
shapefile_directory = os.path.dirname(path) + config[2]
shape_dat_path = os.path.dirname(path) + config[3] # path to SHP.dat

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
file_shp = open(shape_dat_path, 'w')

# core

# loops over all tiff images (now disabled)
# l'idea è quella di permettere all'utente di cliccare un button "next" in una GUI appositamente creata (o di cliccare un tasto specifico)
# una volta terminato di editare l'immagine corrente, per poter proseguire con l'immagine successiva caricata nell'array tiffs (e raws)
#for i in range(len(tiffs)):

# Load Raster
filename = os.path.splitext(os.path.basename(tiffs[0]))[0] # gets the first .tiff file name (without extension)
	
shapefolder = shapefile_directory + '/' + filename # folder that contains shp for every file
if not os.path.exists(shapefolder):
	os.makedirs(shapefolder)

raster = QgsRasterLayer(tiffs[0], filename)
QgsProject.instance().addMapLayer(raster) # .tiff is loaded in the project
entries = []

# Define band
band = QgsRasterCalculatorEntry()
band.ref = filename + '@1'
band.raster = raster
band.bandNumber = 1
entries.append(band)

# Raster calculation process
calc = QgsRasterCalculator(band.ref, tiffs[0], "GTiff", raster.extent(), raster.width(), raster.height(), entries)
calc.processCalculation() # creates a Raster GDAL-compatible (editable), overwrites old tiff file

QgsProject.instance().removeMapLayers([raster.id()]) # tiff is not useful anymore
	
QgsProject.instance().addMapLayer(QgsRasterLayer(raws[0], filename)) # adds raw image to project as raster
	
processing.run(r"gdal:polygonize",
{'INPUT': tiffs[0],
	'BAND': 1,
	'FIELD': 'VEGETATED',
	'EIGHT_CONNECTEDNESS': 1,
	'OUTPUT': shapefolder + "/" + filename + ".shp"}) # generates shp

file_shp.write(shapefolder + "/" + filename + ".shp")
shp = QgsVectorLayer(shapefolder + "/" + filename + ".shp", 'SHP_' + filename, 'ogr')
with edit(shp):
	soil = QgsFeatureRequest().setFilterExpression('"VEGETATED" != 255')
	soil.setSubsetOfAttributes([])
	soil.setFlags(QgsFeatureRequest.NoGeometry)
	for feature in shp.getFeatures(soil):
		shp.deleteFeature(feature.id()) # remove soil

shp.dataProvider().addAttributes([QgsField("CROP", QVariant.Bool), QgsField("TEST", QVariant.Int)]) # adds attributes to the vector layer (test)
shp.updateFields()
QgsProject.instance().addMapLayer(shp) # adds shp to project, to be manually modified

file_shp.close()