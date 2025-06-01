import os
import stat
from datetime import datetime
from logging import getLogger

import cv2
import numpy as np
from common.client import FaceLockClient, GetUserMessage
from common.constants import DEBUG, Extensions
from common.tools import replace_file_extension
from common.user import User
from components.FileDialog.FileDialogUI import Ui_File
from crypto.rsa_crypto_provider import RsaCryptoProvider
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox

logger = getLogger(__name__)


class File:
    def __init__(self, path: str):
        self.path = path
        self.name = os.path.basename(path)
        self.size = os.path.getsize(path)
        self.last_modification_time = datetime.fromtimestamp(os.path.getmtime(path))
        self.creation_time = datetime.fromtimestamp(os.path.getctime(path))
        self.permissions = stat.filemode(os.stat(path).st_mode)
        self.user_id = os.stat(path).st_uid
        try:
            self.extension = Extensions(os.path.splitext(path)[1].lstrip("."))
        except ValueError:
            logger.warning(f"Unknown file extension for {path}, using default icon.")
            self.extension = Extensions.UNKNOWN

    def format_file_size(self) -> str:
        """Returns a human-readable file size."""
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024**2:
            return f"{self.size / 1024:.2f} KB"
        elif self.size < 1024**3:
            return f"{self.size / (1024 ** 2):.2f} MB"
        else:
            return f"{self.size / (1024 ** 3):.2f} GB"


class FileDialog(QtWidgets.QDialog):
    def __init__(self, mainWindow, filepath, user_name: str):
        """Initializes the FileDialog."""
        super(FileDialog, self).__init__()
        self.ui = Ui_File()
        self.ui.setupUi(self)
        self.ui.decryptButton.clicked.connect(self.decrypt_button_click)
        self.ui.encryptButton.clicked.connect(self.encrypt_button_click)
        self.ui.chooseFileButton.clicked.connect(self.choose_another_file)
        self.mainWindow = mainWindow
        self.base_path = os.getcwd()
        self.ui.label_2.setText(self.ui.label_2.text() + user_name)
        self.client = FaceLockClient()
        self.user = self.init_user(user_name)
        self.rsa_provider = RsaCryptoProvider()
        self.file = None
        self.load_file(filepath)

    def choose_file(self):
        """
        Opens QFileDialog to choose a file and loads it.
        """
        file_path = None
        while not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                None, "Chose file", os.getcwd(), "All Files (*);;FaceLock Files (*.fl)"
            )
            if not file_path:
                QMessageBox.critical(None, "Error", "File not selected.")
        return file_path

    def load_file(self, file_path: str):
        """"""
        if file_path is None:
            file_path = self.choose_file()

        abs_file_path = self.get_absolute_path(file_path)
        if not os.path.exists(abs_file_path):
            logger.error(f"File {abs_file_path} does not exist.")
            self.set_file_icon(
                cv2.imread(self.get_absolute_path(Extensions.UNKNOWN.icon_path), -1)
            )
            return
        self.file = File(abs_file_path)
        self.setup_buttons()
        self.setup_labels()

    def init_user(self, user_name: str):
        """Initializes the user based on the provided username."""
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

    def setup_buttons(self):
        """
        Sets up the buttons based on the file type.
        """
        if self.file.extension == Extensions.FL:
            self.ui.encryptButton.setEnabled(False)
            self.ui.decryptButton.setEnabled(True)
            self.ui.encryptButton.setStyleSheet(
                """
                QPushButton {
                    color: gray;
                    background-color: rgba(50, 50, 50, 30);
                    border: none;
                    border-radius: 10px;
                    font-size: 18px;
                }
            """
            )
            self.ui.decryptButton.setStyleSheet(
                """
                QPushButton {
                    color: white;
                    background-color: rgba(0, 0, 0, 30);
                    border: none;
                    border-radius: 10px;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 45);
                }
            """
            )
        else:
            self.ui.encryptButton.setEnabled(True)
            self.ui.decryptButton.setEnabled(False)
            self.ui.encryptButton.setStyleSheet(
                """
                QPushButton {
                    color: white;
                    background-color: rgba(0, 0, 0, 30);
                    border: none;
                    border-radius: 10px;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 45);
                }
            """
            )
            self.ui.decryptButton.setStyleSheet(
                """
                QPushButton {
                    color: gray;
                    background-color: rgba(50, 50, 50, 30);
                    border: none;
                    border-radius: 10px;
                    font-size: 18px;
                }
            """
            )

    def setup_labels(self):
        """Sets up the labels with file information."""
        # Set file icon
        self.file_icon = cv2.imread(
            self.get_absolute_path(self.file.extension.icon_path), -1
        )

        self.set_file_icon(self.file_icon)

        # Filename
        file_name = self.file.name
        if len(file_name) > 24:
            file_name = file_name[:21] + "..."
        self.ui.filenameLabel.setText(file_name)
        # File size
        self.ui.sizeLabel.setText(self.file.format_file_size())

        # Last modification time
        self.ui.lastModLabel.setText(str(self.file.last_modification_time))

        # Creation time
        self.ui.creationLabel.setText(str(self.file.creation_time))

        # UID and permissions
        self.ui.permLabel.setText(str(self.file.permissions))
        self.ui.userLabel.setText(str(self.file.user_id))

    def set_file_icon(self, img: np.ndarray):
        """Sets the file icon in the UI."""
        qt_img = self.convert_cv_qt(img)
        self.ui.fileImgLabel.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Converts OpenCV image to QPixmap."""
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

        with open(self.file.path, "rb") as file:
            file_data = file.read()

        # Save original extension in metadata
        _, ext = os.path.splitext(self.file.path)
        ext = ext.lstrip(".")  # remove dot if present

        metadata_prefix = f"{ext}:::".encode("utf-8")  # delimiter to separate
        payload = metadata_prefix + file_data

        try:
            encrypted_data = self.rsa_provider.encrypt(payload, self.user.public_key)
        except Exception as e:
            logger.exception(f"Encryption error: {e}")
            self.ui.debug_label.setText("Encryption failed due to an error.")
            return

        sha256 = self.rsa_provider.sha256(encrypted_data)

        new_file_path = replace_file_extension(self.file.path, Extensions.FL.value)
        with open(new_file_path, "wb") as new_file:
            new_file.write(encrypted_data)

        logger.info(f"Encrypted file hash: {sha256}")
        self.load_file(new_file_path)
        if DEBUG:
            self.ui.debug_label.setText("Encryption completed successfully.")

    @QtCore.pyqtSlot()
    def decrypt_button_click(self):
        """Decrypts file and restores original extension and logs hash."""
        if not self.user:
            self.ui.debug_label.setText("User not found. Cannot decrypt file.")
            return

        logger.info(f"Decrypt button clicked for user: {self.user.username}")
        private_key = self.user.load_private_key()

        with open(self.file.path, "rb") as file:
            encrypted_data = file.read()

        try:
            decrypted_payload = self.rsa_provider.decrypt(encrypted_data, private_key)
        except ValueError:
            self.ui.debug_label.setText(
                "Decryption failed. You do not have permission to decrypt this file."
            )
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
            original_data = decrypted_payload[prefix_end + 3 :]
        except ValueError:
            self.ui.debug_label.setText("Invalid encrypted format.")
            return

        new_file_path = replace_file_extension(self.file.path, original_ext)

        with open(new_file_path, "wb") as new_file:
            new_file.write(original_data)

        logger.info(f"Decrypted file hash: {sha256}")
        self.load_file(new_file_path)
        if DEBUG:
            self.ui.debug_label.setText("Decryption completed successfully.")

    @QtCore.pyqtSlot()
    def choose_another_file(self):
        """
        Opens QFileDialog to choose a different file and reloads the UI.
        """
        file_path = self.choose_file()
        self.load_file(file_path)
