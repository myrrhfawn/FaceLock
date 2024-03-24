import os
import queue
import sys
import cv2
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from MainWindow.MainWindow import Ui_MainWindow
from fl_utils.base_logging import setup_logging
from logging import getLogger
from app.stream.video_stream import VideoStream
from app.stream.video_pipeline import GStreamerPipeline
import numpy as np

setup_logging(file_name="app.log")
logger = getLogger(__name__)


class FaceLockApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(FaceLockApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.logic = 0
        self.value = 1
        self.disply_width = 540
        self.display_height = 280

        self.video_queue = queue.Queue()
        #self.video_stream = VideoStream(0, self.video_queue)
        self.video_stream = GStreamerPipeline()

        self.ui.pushButton.clicked.connect(self.show_video_stream)

    def change_label_text(self, text):
        pass

    @QtCore.pyqtSlot()
    def show_video_stream(self):
        logger.info("Show video stream")
        self.video_stream.start()
        while True:
            if self.video_stream.isFrameReady():
                np_img = self.video_stream.get_frame(detection=True)
                self.update_image(np_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.video_stream.stop()

    @QtCore.pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.ui.videoLabel.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, QtCore.Qt.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(p)

    def displayImage(self, frame):
        qformat = QtGui.QImage.Format.Format_Indexed8

        if len(frame.shape) == 3:
            if frame.shape[2] == 4:
                qformat = QtGui.QImage.Format.Format_RGBA8888
            else:
                qformat = QtGui.QImage.Format.Format_RGB888
        logger.info("set pixmap")
        image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], qformat)
        image = image.rgbSwapped()
        self.ui.videoLabel.setPixmap(QtGui.QPixmap.fromImage(image))
        self.ui.videoLabel.setMinimumWidth(frame.shape[1])
        self.ui.videoLabel.setMinimumHeight(frame.shape[0])
        self.ui.videoLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)


def main():
    argv = sys.argv[1:]
    print(f"argv: {argv}")
    app = QtWidgets.QApplication(sys.argv)
    window = FaceLockApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
