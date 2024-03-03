import queue
import sys
import cv2
import time
from PySide6 import QtCore
from PySide6.QtCore import Slot, QPointF, Qt, QRectF
from PySide6.QtGui import QImage, QPixmap, QPolygonF, QPainter, QPen, QColor, QBrush
from PySide6.QtWidgets import QApplication, QMainWindow
from MainWindow.MainWindow import Ui_MainWindow
from fl_utils.base_logging import setup_logging
from logging import getLogger
from app.stream.video_stream import VideoStream
setup_logging(file_name="app.log")
logger = getLogger(__name__)


class FaceLockApp(QMainWindow):
    def __init__(self):
        super(FaceLockApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.logic = 0
        self.value = 1
        self.video_queue = queue.Queue()
        self.video_stream = VideoStream(0, self.video_queue)
        self.ui.pushButton.clicked.connect(self.show_video_stream)
        #self.show_video_stream()

    def change_label_text(self, text):
        pass #self.ui.label.setText(str(DEBUG))

    @Slot()
    def show_video_stream(self):
        logger.info("Show video stream")
        self.video_stream.start()
        while True:
            if not self.video_queue.empty():
                frame = self.video_queue.get()["frame"]

                self.displayImage(frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        self.video_stream.stop()

    def displayImage(self, frame):
        qformat = QImage.Format.Format_Indexed8

        if len(frame.shape) == 3:
            if frame.shape[2] == 4:
                qformat = QImage.Format.Format_RGBA8888
            else:
                qformat = QImage.Format.Format_RGB888
        logger.info("set pixmap")
        image = QImage(frame, frame.shape[1], frame.shape[0], qformat)
        image = image.rgbSwapped()
        self.ui.videoLabel.setPixmap(QPixmap.fromImage(image))
        self.ui.videoLabel.setMinimumWidth(frame.shape[1])
        self.ui.videoLabel.setMinimumHeight(frame.shape[0])
        self.ui.videoLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        cv2.imshow("", frame)
        cv2.destroyAllWindows()

def main():
    argv = sys.argv[1:]
    print(f"argv: {argv}")
    app = QApplication(sys.argv)
    window = FaceLockApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
