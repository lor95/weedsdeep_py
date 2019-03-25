import os
import pathlib
import processing
import qgis.utils
from qgis.gui import QgsMessageBar
from qgis.core import *
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from .resources import *
from .weedsdeep_processing_dialog import WeedsDeepDialog

class WeedsDeep:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'WeedsDeep_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&QGIS - WeedsDeep')

    def tr(self, message):
        return QCoreApplication.translate('WeedsDeep', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        icon_path = ':/plugins/weedsdeep_processing/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'WeedsDeep: generate and manage shapefiles.'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&QGIS - WeedsDeep'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        self.dlg = WeedsDeepDialog()
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        if result:

            # initialization            
            # set paths
            raw_dat_path = self.dlg.rawdat_browser.filePath()
            tiff_dat_path = self.dlg.tiffdat_browser.filePath()
            shape_dat_directory = self.dlg.shpdat_browser.filePath()
            shapefile_directory = self.dlg.shpfolder_browser.filePath()
            
            # set project crs
            crs = QgsCoordinateReferenceSystem('EPSG:32633')
            QgsProject.instance().setCrs(crs)
            
            # read data
            if not os.path.exists(shapefile_directory):
                os.makedirs(shapefile_directory)
            
            raws = []
            tiffs = []
            shapes = [] # array of vector layers

            file_raw = open(raw_dat_path, 'r')
            for line in file_raw:
                raws.append(line.strip())
            file_raw.close()
            file_tiff = open(tiff_dat_path, 'r')
            for line in file_tiff:
                tiffs.append(line.strip())
            file_tiff.close()
            file_shp = open(shape_dat_directory + '/SHP.dat', 'w')

            # core
            # loops over all tiff images
            for i in range(len(tiffs)):
                # Load Rasters
                filename = os.path.splitext(os.path.basename(tiffs[i]))[0] # gets the first .tiff file name (without extension)
                raster_directory = os.path.dirname(tiffs[i])
                shapefolder = shapefile_directory + '/' + filename # folder that contains shp for every file
                if not os.path.exists(shapefolder):
                    os.makedirs(shapefolder)
                
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

                data = QgsVectorLayer(str(pathlib.Path(raster_directory).as_uri()) + '/' + filename + '.csv?delimiter=;', 'CSV_' + filename, 'delimitedtext') # add csv layer to get data from
                QgsProject.instance().addMapLayer(data)
                join = QgsVectorLayerJoinInfo()
                join.setJoinFieldName('id')
                join.setTargetFieldName('id')
                join.setJoinLayerId(data.id())
                join.setUsingMemoryCache(True)
                join.setJoinLayer(data)
                shp.addJoin(join)

            self.iface.messageBar().clearWidgets()
            self.iface.messageBar().pushMessage('Done loading...', level = 0, duration = 5)
            file_shp.close()
