# REQUIRED QGIS >= 3

import os
import processing
import qgis.utils
from qgis.core import *
from PyQt5 import QtWidgets
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

# core

# loops over all tiff images
for i in range(1):# loops over the first image only ---> for i in range(len(tiffs)):

	# Load Raster
	filename = os.path.splitext(os.path.basename(tiffs[i]))[0] # gets the first .tiff file name (without extension)
	
	shapefolder = shapefile_directory + '/' + filename # folder that contains shp for every file
	if not os.path.exists(shapefolder):
		os.makedirs(shapefolder)

	raster = QgsRasterLayer(tiffs[i], filename)
	QgsProject.instance().addMapLayer(raster) # .tiff is loaded in the project
	entries = []

	# Define band
	band = QgsRasterCalculatorEntry()
	band.ref = filename + '@1'
	band.raster = raster
	band.bandNumber = 1
	entries.append(band)

	# Raster calculation process
	calc = QgsRasterCalculator(band.ref, tiffs[i], "GTiff", raster.extent(), raster.width(), raster.height(), entries)
	calc.processCalculation() # creates a Raster GDAL-compatible (editable), overwrites old tiff file
	
	QgsProject.instance().removeMapLayers([raster.id()]) # tiff is not useful anymore
	
	QgsProject.instance().addMapLayer(QgsRasterLayer(raws[i], filename)) # adds raw image to project as raster
	
	processing.run(r"gdal:polygonize",
	{'INPUT': tiffs[i],
		'BAND': 1,
		'FIELD': 'VEGETATED',
		'EIGHT_CONNECTEDNESS': 1,
		'OUTPUT': shapefolder + "/" + filename + ".shp"}) # generates shp

	shp = QgsVectorLayer(shapefolder + "/" + filename + ".shp", 'SHP_' + filename, 'ogr')
	with edit(shp):
		soil = QgsFeatureRequest().setFilterExpression('"VEGETATED" != 255')
		soil.setSubsetOfAttributes([])
		soil.setFlags(QgsFeatureRequest.NoGeometry)
		for feature in shp.getFeatures(soil):
			shp.deleteFeature(feature.id()) # remove soil
	
	data = shp.dataProvider() # gets attributes of the vector layer (unused)

	QgsProject.instance().addMapLayer(shp) # adds shp to project, to be manually modified