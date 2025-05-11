import cv2
import stat
from PyQt5 import QtCore, QtGui, QtWidgets
from app.components.FileDialog.FileDialogUI import Ui_File
from logging import getLogger
from app.constants import DEFAULT_FILE_ICON_PATH, FL_FILE_ICON_PATH, Extensions
import numpy as np
import os
from datetime import datetime

logger = getLogger(__name__)


class FileDialog(QtWidgets.QDialog):
    def __init__(self, mainWindow, filepath, user):
        super(FileDialog, self).__init__()
        self.ui = Ui_File()
        self.ui.setupUi(self)
        self.ui.decryptButton.clicked.connect(self.decrypt_button_click)
        self.ui.encryptButton.clicked.connect(self.encrypt_button_click)
        self.mainWindow = mainWindow
        self.file_path = filepath
        self.file_icon = cv2.imread(DEFAULT_FILE_ICON_PATH, -1)
        self.ui.label_2.setText(self.ui.label_2.text() + user)
        self.setup_labels()

    def setup_labels(self):

        # Set file icon
        ext = self.file_path.split(".")[-1]

        if Extensions(ext) == Extensions.FL:
            self.file_icon = cv2.imread(FL_FILE_ICON_PATH, -1)
        else:
            self.file_icon = cv2.imread(DEFAULT_FILE_ICON_PATH, -1)
        self.set_file_icon(self.file_icon)

        # Filename
        self.ui.filenameLabel.setText(self.file_path.split("/")[-1])
        self.ui.sizeLabel.setText(
            str(os.path.getsize(self.file_path) / (1024 * 1024)) + " GB"
        )

        # Last modification time
        modification_time = os.path.getmtime(self.file_path)
        readable_mod_time = datetime.fromtimestamp(modification_time)
        self.ui.lastModLabel.setText(str(readable_mod_time))

        # Creation time
        creation_time = os.path.getctime(self.file_path)
        readable_cr_time = datetime.fromtimestamp(creation_time)
        self.ui.creationLabel.setText(str(readable_cr_time))

        # UID and permissions
        file_stat = os.stat(self.file_path)
        permissions = stat.filemode(file_stat.st_mode)
        self.ui.permLabel.setText(str(permissions))
        self.ui.userLabel.setText(str(file_stat.st_uid))

    def set_file_icon(self, img: np.ndarray):
        qt_img = self.convert_cv_qt(img)
        self.ui.fileImgLabel.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        if cv_img.shape[2] == 4:
            rgba_image = cv2.cvtColor(cv_img, cv2.COLOR_BGRA2RGBA)
            h, w, ch = rgba_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QtGui.QImage(
                rgba_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGBA8888
            )
        else:
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QtGui.QImage(
                rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888
            )

        p = convert_to_Qt_format.scaled(256, 256, QtCore.Qt.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(p)

    @QtCore.pyqtSlot()
    def encrypt_button_click(self):
        pass

    @QtCore.pyqtSlot()
    def decrypt_button_click(self):
        pass
