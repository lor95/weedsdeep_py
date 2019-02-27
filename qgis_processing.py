# Only works with QGIS >= 3 

import qgis.utils
from qgis.core import *
from pathlib import Path
from PyQt5 import QtWidgets
#from qgis.gui import QgsMapLayerActionRegistry
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
#from osgeo import gdal, ogr, osr

# Load input dialog
qid = QtWidgets.QInputDialog()
title = "qgis_processing"
label = "Enter path .TIFF:"
mode = QtWidgets.QLineEdit.Normal
path, res = QtWidgets.QInputDialog.getText(qid, title, label, mode)

# Load Raster
qgis.utils.iface.addRasterLayer(path, "tiff_img") ###############
layer = qgis.utils.iface.activeLayer()
entries = []

# Define band1
band = QgsRasterCalculatorEntry()
band.ref = 'tiff_img@1'
band.raster = layer
band.bandNumber = 1
entries.append(band)

# Raster calculation process
calc = QgsRasterCalculator(band.ref, path, "GTiff", layer.extent(), layer.width(), layer.height(), entries)
calc.processCalculation()

# Load Raster
#qgis.utils.iface.addRasterLayer(path, "calc_raster")

#######################################################################
test = Path(path).parent/"test.shp"
#sourceRaster = gdal.Open(test)
#sr_proj=sourceRaster.GetProjection()
#raster_proj = osr.SpatialReference()
#raster_proj.ImportFromWkt(sr_proj)

#band = sourceRaster.GetRasterBand(1) 
#bandArray = band.ReadAsArray()
#outShapefile = "POLYGON"
#driver = ogr.GetDriverByName("ESRI Shapefile")
#outDatasource = driver.CreateDataSource(outShapefile+ ".shp")
#outLayer = outDatasource.CreateLayer('polygonized', srs=raster_proj)
#print(outLayer)
#newField = ogr.FieldDefn(str(1), ogr.OFTInteger)
#outLayer.CreateField(newField)

############################################################################

#gdal.Polygonize(path, path, Path(path).parent/"test.shp", 1)