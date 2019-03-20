# REQUIRED QGIS >= 3

import os
import pathlib
import processing
import qgis.utils
from qgis.core import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import QVariant
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry

# Load input dialog -> to be removed
qid = QtWidgets.QInputDialog()
title = 'qgis_processing'
label = 'Enter config-qgis.ini path:'
mode = QtWidgets.QLineEdit.Normal
path, res = QtWidgets.QInputDialog.getText(qid, title, label, mode) # path -> path to config-qgis.ini

# initialization

crs = QgsCoordinateReferenceSystem('EPSG:32633')
QgsProject.instance().setCrs(crs)

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
raster_directory = os.path.dirname(path) + config[4] # path to rasters

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

shapes = [] # array of vector layers

# core

# loops over all tiff images
for i in range(len(tiffs)):

    # Load Raster
    filename = os.path.splitext(os.path.basename(tiffs[i]))[0] # gets the first .tiff file name (without extension)

    shapefolder = shapefile_directory + '/' + filename # folder that contains shp for every file
    if not os.path.exists(shapefolder):
        os.makedirs(shapefolder)

    #raster = QgsRasterLayer(tiffs[i], filename)
    #raster.setCrs(crs)
    #QgsProject.instance().addMapLayer(raster) # .tiff is loaded in the project
    #entries = []

    # Define band
    #band = QgsRasterCalculatorEntry()
    #band.ref = filename + '@1'
    #band.raster = raster
    #band.bandNumber = 1
    #entries.append(band)

    # Raster calculation process
    #calc = QgsRasterCalculator(band.ref, tiffs[i], 'GTiff', raster.extent(), raster.width(), raster.height(), entries)
    #calc.processCalculation() # creates a Raster GDAL-compatible (editable), overwrites old tiff file

    #QgsProject.instance().removeMapLayers([raster.id()])
	
    raw = QgsRasterLayer(raws[i], filename)
    raw.setCrs(crs)
    QgsProject.instance().addMapLayer(raw) # adds raw image to project as raster
	
    processing.run('gdal:polygonize',
    {'INPUT': tiffs[i],
        'BAND': 1,
        'FIELD': 'id',
        'EIGHT_CONNECTEDNESS': 1,
        'OUTPUT': shapefolder + '/' + filename + '.shp'}) # generates shp

    file_shp.write(shapefolder + '/' + filename + '.shp\n')
    shp = QgsVectorLayer(shapefolder + '/' + filename + '.shp', 'SHP_' + filename, 'ogr')
    shp.setCrs(crs)
    with edit(shp):
        soil = QgsFeatureRequest().setFilterExpression('"id" = 0')
        soil.setSubsetOfAttributes([])
        soil.setFlags(QgsFeatureRequest.NoGeometry)
        for feature in shp.getFeatures(soil):
            shp.deleteFeature(feature.id()) # remove soil

    shp.dataProvider().addAttributes([QgsField('area', QVariant.Double), QgsField('perimeter', QVariant.Double)]) # adds attributes to the vector layer (test)
    shp.updateFields()
    area = shp.fields().indexFromName('area')
    perimeter = shp.fields().indexFromName('perimeter')
    shp.startEditing()
    e0 = QgsExpression("""$area""")
    e1 = QgsExpression("""$perimeter""")
    c = QgsExpressionContext()
    s = QgsExpressionContextScope()
    s.setFields(shp.fields())
    c.appendScope(s)
    e0.prepare(c)
    e1.prepare(c)
    
    for feature in shp.getFeatures():
        c.setFeature(feature)
        shp.dataProvider().changeAttributeValues({feature.id():{
            area: e0.evaluate(c),
            perimeter: e1.evaluate(c)}})
    shp.commitChanges()
    shapes.append(shp)
    QgsProject.instance().addMapLayer(shp) # adds shp to project, to be manually modified

    data = QgsVectorLayer(str(pathlib.Path(raster_directory).as_uri()) + '/' + filename + '.csv?delimiter=;', 'csv', 'delimitedtext') # add csv layer to get data from
    QgsProject.instance().addMapLayer(data)
    join = QgsVectorLayerJoinInfo()
    join.setJoinFieldName('id')
    join.setTargetFieldName('id')
    join.setJoinLayerId(data.id())
    join.setUsingMemoryCache(True)
    join.setJoinLayer(data)
    shp.addJoin(join)

# merge vectors and load
#processing.run('qgis:mergevectorlayers',
#    {'LAYERS': shapes,
#        'CRS': 'EPSG:32633',
#        'OUTPUT': shapefile_directory + '/OUTPUT.shp'})
#QgsProject.instance().addMapLayer(QgsVectorLayer(shapefile_directory + '/OUTPUT.shp', 'OUTPUT', 'ogr'))
#file_shp.write(shapefile_directory + '/OUTPUT.shp\n')
file_shp.close()