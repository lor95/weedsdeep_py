# Only works with QGIS >= 3 

import qgis.utils
from qgis.core import *
from pathlib import Path
from PyQt5 import QtWidgets # QGIS >= 3
#from qgis.gui import QgsMapLayerActionRegistry
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
from osgeo import gdal, ogr#, osr

# Load input dialog
qid = QtWidgets.QInputDialog()
title = "qgis_processing"
label = "Enter TIFF path:"
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
calc.processCalculation() # creates a Raster GDAL-compatible (editable), overwrites old tiff file

# Load Raster
#qgis.utils.iface.addRasterLayer(path, "calc_raster")

#########################no##############################################

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

#dst_layername = 'polygonized_test_all_all_2.shp'
#drv = ogr.GetDriverByName("ESRI Shapefile")
#dst_ds = drv.CreateDataSource(dst_layername)
#dst_layer = dst_ds.CreateLayer(dst_layername, None)
#fd = ogr.FieldDefn("DN", ogr.OFTInteger)
#dst_layer.CreateField(fd)
#dst_field = dst_layer.GetLayerDefn().GetFieldIndex("DN")
#gdal.Polygonize(path, path, dst_layer, dst_field, [], callback=None)

#################################################################################

gdal.UseExceptions()
src_ds = gdal.Open(path)
if src_ds is None:
    print('Unable to open %s' % src_filename)
    sys.exit(1)

try:
    srcband = src_ds.GetRasterBand(1)
except(RuntimeError, e):
    print(e)
    sys.exit(1)

dst_layername = "POLYGONIZED"
drv = ogr.GetDriverByName("ESRI Shapefile")
dst_ds = drv.CreateDataSource(dst_layername + ".shp")
dst_layer = dst_ds.CreateLayer(dst_layername, srs = None)

# gdal.Polygonize(srcband, None, dst_layer, -1, [], callback=None)

############################################################################

#gdal.Polygonize(path, path, Path(path).parent/"test.shp", 1)

## shell command: python3 -m gdal_polygonize path\to\test.tiff path\to\OUTPUT.shp -b 1 -f "ESRI Shapefile" OUTPUT DN -mask path\to\test.tiff