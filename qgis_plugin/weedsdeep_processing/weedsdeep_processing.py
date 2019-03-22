import os
import pathlib
import processing
import qgis.utils
from qgis.core import *
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .weedsdeep_processing_dialog import WeedsDeepDialog
import os.path


class WeedsDeep:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
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
        self.menu = self.tr(u'&QGIS WeedsDeep')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
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
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/weedsdeep_processing/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'WeedsDeep'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&QGIS WeedsDeep'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = WeedsDeepDialog()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            crs = QgsCoordinateReferenceSystem('EPSG:32633')
            QgsProject.instance().setCrs(crs)
            ########################################################################################
            raw_dat_path = 'C:\\Users\\Lorenzo\\Dropbox\\weedsdeep_py\\data\\RAW.dat'
            tiff_dat_path = 'C:\\Users\\Lorenzo\\Dropbox\\weedsdeep_py\\data\\TIFF.dat'
            shape_dat_directory = 'C:\\Users\\Lorenzo\\Dropbox\\weedsdeep_py\\data'
            shapefile_directory = 'C:\\Users\\Lorenzo\\Dropbox\\weedsdeep_py\\img\\shapefiles'
            
            ###################################################################
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
            file_shp = open(shape_dat_directory + '/SHP.dat', 'w')

            shapes = [] # array of vector layers

            # core

            # loops over all tiff images
            for i in range(len(tiffs)):
                # Load Raster
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

                file_shp.write(shapefolder + '\n')
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

            file_shp.close()
