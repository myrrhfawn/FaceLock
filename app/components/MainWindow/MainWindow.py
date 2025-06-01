import queue
import time
from collections import deque
from logging import getLogger

import cv2
from common.base_logging import setup_logging
from common.constants import UNKNOWN_TITLE
from common.frame import Frame
from common.tools import prepare_image
from components.FileDialog.FileDialog import FileDialog
from components.MainWindow.MainWindowUI import Ui_MainWindow
from components.RegisterDialog.RegisterDialog import RegisterDialog
from components.video_stream.VideoStreamWorker import VideoStreamWorker
from PyQt5 import QtCore, QtGui, QtWidgets

setup_logging(file_name="app.log")
logger = getLogger(__name__)


def round_corners(widget, radius=34):
    """Apply rounded corners to a widget."""
    path = QtGui.QPainterPath()
    rect = QtCore.QRectF(widget.rect())  # <-- виправлено тут
    path.addRoundedRect(rect, radius, radius)
    region = QtGui.QRegion(path.toFillPolygon().toPolygon())
    widget.setMask(region)


class UnknownDetectionBuffer:
    def __init__(self, time_window_sec=3, count_threshold=15):
        self.detections = deque()
        self.time_window = time_window_sec
        self.threshold = count_threshold

    def add_detection(self):
        """Add a new detection timestamp."""
        now = time.time()
        self.detections.append(now)
        self._cleanup_old(now)

    def _cleanup_old(self, now):
        """Remove old detections that are outside the time window."""
        while self.detections and now - self.detections[0] > self.time_window:
            self.detections.popleft()

    def should_enable_signup(self):
        """Return True if enough recent unknown detections occurred."""
        now = time.time()
        self._cleanup_old(now)
        return len(self.detections) >= self.threshold

    def reset(self):
        """Clear all detections (e.g., after user signs up)."""
        self.detections.clear()


class FaceLockApp(QtWidgets.QMainWindow):
    def __init__(self, filepath: str = None):
        super(FaceLockApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.filepath = filepath
        self.video_queue = queue.Queue()

        self.ui.signupButton.hide()
        self.ui.signinButton.clicked.connect(self.sign_in)
        self.ui.signinButton.hide()
        self.ui.signupButton.clicked.connect(self.register_user)
        self.user_last_det = None
        self.unknown_detection_buffer = UnknownDetectionBuffer()

        self.stream = VideoStreamWorker()
        self.stream.set_reload_true()
        self.stream.frame_ready.connect(self.update_image)

    @QtCore.pyqtSlot()
    def sign_in(self):
        """Handle user sign-in."""
        logger.info("Sign in...")
        if self.user_last_det is not None:
            self.hide()
            fileWindow = FileDialog(
                mainWindow=self, filepath=self.filepath, user_name=self.user_last_det
            )
            fileWindow.show()
            fileWindow.exec()
        else:
            self.ui.debug_label.setText("No face detected. Try Again")

    @QtCore.pyqtSlot()
    def register_user(self):
        """Handle user registration."""
        logger.info("Register user...")
        frame = Frame()
        while frame.detection != UNKNOWN_TITLE:
            frame = self.stream.get_frame()
        encoding = prepare_image(frame.img, encoding=True)
        if len(encoding) > 0:
            encoding = encoding[0]
        if len(encoding) == 0:
            self.ui.debug_label.setText("No face detected. Try Again")
            logger.info("No face detected. Try Again")
            return

        registerDialog = RegisterDialog(mainWindow=self, encoding=encoding)
        self.hide()
        registerDialog.show()
        registerDialog.exec()

    @QtCore.pyqtSlot(Frame)
    def update_image(self, frame: Frame):
        """Update the displayed image in the UI."""
        qt_img = self.convert_cv_qt(frame.img)
        round_corners(self.ui.videoLabel)
        self.ui.videoLabel.setPixmap(qt_img)

        if frame.detection == UNKNOWN_TITLE:
            self.unknown_detection_buffer.add_detection()
            if self.unknown_detection_buffer.should_enable_signup():
                self.ui.signinButton.hide()
                self.user_last_det = None
        else:
            logger.info(f"Detected user: {frame.detection}")
            self.user_last_det = frame.detection
            self.ui.signinButton.show()
            self.unknown_detection_buffer.reset()

        if self.ui.signinButton.isHidden():
            self.ui.signupButton.show()
        else:
            self.ui.signupButton.hide()

    def convert_cv_qt(self, cv_img):
        """Convert OpenCV image to QPixmap for display in the UI."""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(
            rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888
        )
        p = convert_to_Qt_format.scaled(w, h, QtCore.Qt.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(p)

    def closeEvent(self, event):
        """""" ""
        self.stream.stop()
        self.thread.quit()
        self.thread.wait()
        self.video_stream.stop()
        super().closeEvent(event)

    def hide(self):
        """
        Hides the main window.
        """
        self.stream.stop_pipeline()
        super().hide()

    def show(self):
        """Shows the main window and starts the video stream pipeline."""
        self.stream.start_pipeline()
        super().show()
