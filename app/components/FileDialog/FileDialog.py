import cv2
import stat

from PyQt5 import QtCore, QtGui, QtWidgets
from fsspec.asyn import private
from pyarrow.ipc import new_file

from app.client import FaceLockClient, GetUserMessage
from app.common.User import User
from app.common.tools import replace_file_extension
from app.components.FileDialog.FileDialogUI import Ui_File
from logging import getLogger
from app.constants import DEFAULT_FILE_ICON_PATH, FL_FILE_ICON_PATH, Extensions
import numpy as np
import os
from datetime import datetime

from app.crypto.rsa_crypto_provider import RsaCryptoProvider

logger = getLogger(__name__)


class FileDialog(QtWidgets.QDialog):
    def __init__(self, mainWindow, filepath, user_name: str):
        """ Initializes the FileDialog."""
        super(FileDialog, self).__init__()
        self.ui = Ui_File()
        self.ui.setupUi(self)
        self.ui.decryptButton.clicked.connect(self.decrypt_button_click)
        self.ui.encryptButton.clicked.connect(self.encrypt_button_click)
        self.mainWindow = mainWindow
        self.base_path = os.getcwd()
        self.ui.label_2.setText(self.ui.label_2.text() + user_name)
        self.client = FaceLockClient()
        self.user = self.init_user(user_name)
        self.rsa_provider = RsaCryptoProvider()
        self.file_path = None
        self.load_file(filepath)

    def load_file(self, file_path: str):
        self.file_path = self.get_absolute_path(file_path)
        if not os.path.exists(self.file_path):
            logger.error(f"File {self.file_path} does not exist.")
            self.set_file_icon(
                cv2.imread(self.get_absolute_path(Extensions.UNKNOWN.icon_path), -1)
            )
            return

        self.setup_labels()

    def init_user(self, user_name: str):
        message = GetUserMessage(username=user_name)
        response = self.client.send_message(message)
        if response and response["status"] == 200:
            user_data = self.client.get_data(response)
            if not user_data:
                logger.error("User data is empty. Cannot initialize user.")
                return None
            return User(**user_data)

    def get_absolute_path(self, relative_path: str) -> str:
        """
        Returns absolute path to the file.
        """
        return os.path.abspath(os.path.join(self.base_path, relative_path))

    def setup_labels(self):
        # Set file icon

        ext = self.file_path.split(".")[-1]

        if Extensions(ext) == Extensions.FL:
            self.file_icon = cv2.imread(self.get_absolute_path(FL_FILE_ICON_PATH), -1)
        else:
            self.file_icon = cv2.imread(self.get_absolute_path(DEFAULT_FILE_ICON_PATH), -1)

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
        """Encrypts file and saves original extension and hash."""
        if not self.user:
            self.ui.debug_label.setText("User not found. Cannot encrypt file.")
            return

        logger.info(f"Encrypt button clicked for user: {self.user.username}")

        with open(self.file_path, "rb") as file:
            file_data = file.read()

        # Save original extension in metadata
        _, ext = os.path.splitext(self.file_path)
        ext = ext.lstrip(".")  # remove dot if present

        metadata_prefix = f"{ext}:::".encode("utf-8")  # delimiter to separate
        payload = metadata_prefix + file_data

        encrypted_data = self.rsa_provider.encrypt(payload, self.user.public_key)
        sha256 = self.rsa_provider.sha256(encrypted_data)

        new_file_path = replace_file_extension(self.file_path, Extensions.FL.value)
        with open(new_file_path, "wb") as new_file:
            new_file.write(encrypted_data)

        logger.info(f"Encrypted file hash: {sha256}")
        self.load_file(new_file_path)
        self.ui.debug_label.setText("Encryption completed successfully.")

    @QtCore.pyqtSlot()
    def decrypt_button_click(self):
        """Decrypts file and restores original extension and logs hash."""
        if not self.user:
            self.ui.debug_label.setText("User not found. Cannot decrypt file.")
            return

        logger.info(f"Decrypt button clicked for user: {self.user.username}")
        private_key = self.user.load_private_key()

        with open(self.file_path, "rb") as file:
            encrypted_data = file.read()

        try:
            decrypted_payload = self.rsa_provider.decrypt(encrypted_data, private_key)
        except ValueError:
            self.ui.debug_label.setText("Decryption failed. You do not have permission to decrypt this file.")
            return
        except Exception as e:
            logger.exception(f"Decryption error: {e}")
            self.ui.debug_label.setText("Decryption failed due to an error.")
            return

        sha256 = self.rsa_provider.sha256(decrypted_payload)

        # Extract metadata and content
        try:
            prefix_end = decrypted_payload.index(b":::")
            original_ext = decrypted_payload[:prefix_end].decode("utf-8")
            original_data = decrypted_payload[prefix_end + 3:]
        except ValueError:
            self.ui.debug_label.setText("Invalid encrypted format.")
            return

        new_file_path = replace_file_extension(self.file_path, original_ext)

        with open(new_file_path, "wb") as new_file:
            new_file.write(original_data)

        logger.info(f"Decrypted file hash: {sha256}")
        self.load_file(new_file_path)
        self.ui.debug_label.setText("Decryption completed successfully.")
