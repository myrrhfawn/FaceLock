import queue
import time

import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from app.components.MainWindow.MainWindowUI import Ui_MainWindow
from app.components.RegisterDialog.RegisterDialog import RegisterDialog
from app.components.FileDialog.FileDialog import FileDialog
from fl_utils.base_logging import setup_logging
from logging import getLogger
from app.stream.video_pipeline import GStreamerPipeline
from app.common.frame import Frame
from app.constants import UNKNOWN_TITLE, REGISTER_BUTTON_TIMEOUT
from app.detector.simple_facerec import SimpleFaceRec
import numpy as np

setup_logging(file_name="app.log")
logger = getLogger(__name__)


class FaceLockApp(QtWidgets.QMainWindow):
    def __init__(self, filepath: str = None):
        super(FaceLockApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.filepath = filepath
        self.video_queue = queue.Queue()
        self.video_stream = GStreamerPipeline()
        self.ui.signupButton.hide()
        self.ui.signinButton.clicked.connect(self.sign_in)
        self.ui.signinButton.hide()
        self.ui.signupButton.clicked.connect(self.register_user)
        self.unknown_det_time = time.time()
        self.user_last_det = None



    def change_label_text(self, text):
        pass

    @QtCore.pyqtSlot()
    def sign_in(self):
        logger.info("Sign in...")
        if self.user_last_det is not None:
            fileWindow = FileDialog(mainWindow=self, filepath=self.filepath, user=self.user_last_det)
            self.hide()
            fileWindow.show()
            fileWindow.exec()
        else:
            self.ui.debug_label.setText("No face detected. Try Again")



    @QtCore.pyqtSlot()
    def register_user(self):
        logger.info("Register user...")
        frame = Frame()
        while frame.detection != UNKNOWN_TITLE:
            if self.video_stream.isFrameReady():
                frame = self.video_stream.get_frame(detection=True, show_det=False)
        encoding = SimpleFaceRec.prepare_image(frame.img, encoding=True)
        if len(encoding) > 0:
            encoding = encoding[0]
        else:
            self.ui.debug_label.setText("No face detected. Try Again")
            return
        registerDialog = RegisterDialog(mainWindow=self, encoding=encoding)
        self.hide()
        registerDialog.show()
        registerDialog.exec()

    def show_video_stream(self):
        logger.info("Show video stream")
        self.video_stream.start()
        while True:
            if self.video_stream.isFrameReady():
                frame = self.video_stream.get_frame(detection=True)
                if frame.detection == UNKNOWN_TITLE:
                    self.user_det_time = time.time()
                else:
                    logger.info(f"USER TIME: {frame.detection}")
                    self.user_last_det = frame.detection
                    self.ui.signinButton.show()

                self.update_image(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if (time.time() - self.unknown_det_time) > REGISTER_BUTTON_TIMEOUT:
                if not self.ui.signinButton.isHidden():
                    self.ui.signupButton.hide()
                else:
                    self.ui.signupButton.show()
        self.video_stream.stop()

    @QtCore.pyqtSlot(np.ndarray)
    def update_image(self, frame: Frame):
        qt_img = self.convert_cv_qt(frame.img)
        self.ui.videoLabel.setMinimumWidth(frame.img.shape[1])
        self.ui.videoLabel.setMinimumHeight(frame.img.shape[0])
        self.ui.videoLabel.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(cv_img.shape[0], cv_img.shape[1], QtCore.Qt.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(p)

    def closeEvent(self, event):
        self.video_stream.stop()
