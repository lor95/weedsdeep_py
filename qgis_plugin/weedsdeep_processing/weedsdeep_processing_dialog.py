import os
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialogButtonBox
from qgis.gui import QgsFileWidget

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'weedsdeep_processing_dialog_base.ui'))

class WeedsDeepDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(WeedsDeepDialog, self).__init__(parent)
        self.setupUi(self) 
        # initialization
        self.shpfolder_browser.setStorageMode(QgsFileWidget.StorageMode.GetDirectory)
        self.shpdat_browser.setStorageMode(QgsFileWidget.StorageMode.GetDirectory)
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        # set signals
        self.rawdat_browser.fileChanged.connect(self.enableButton)
        self.tiffdat_browser.fileChanged.connect(self.enableButton)
        self.shpdat_browser.fileChanged.connect(self.enableButton)
        self.shpfolder_browser.fileChanged.connect(self.enableButton)

    def enableButton(self):
        if os.path.exists(self.rawdat_browser.filePath()) and os.path.exists(self.tiffdat_browser.filePath()) and os.path.exists(self.shpdat_browser.filePath()) and os.path.exists(self.shpfolder_browser.filePath()):
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)