import sys
import time
import cv2
import numpy as np

from PySide6 import QtCore
from PySide6.QtCore import Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow
from constants import DEBUG
from MainWindow.MainWindow import Ui_MainWindow
from fl_utils.base_logging import setup_logging
from logging import getLogger

setup_logging(file_name="server.log")
logger = getLogger(__name__)

class FaceLockApp(QMainWindow):
    def __init__(self):
        super(FaceLockApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.logic = 0
        self.value = 1
        self.ui.pushButton.clicked.connect(self.show_video_stream)
        self.show_video_stream()

    def change_label_text(self, text):
        pass #self.ui.label.setText(str(DEBUG))

    @Slot()
    def show_video_stream(self):
        cap = cv2.VideoCapture(0)

        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                logger.info("get frame")
                image = self.prepare_image(frame)
                cv2.imshow("test", image)
                self.displayImage(frame)
                cv2.waitKey(1)
            else:
                logger.info("No input image")
        cap.release()
        cv2.destroyAllWindows()

    def displayImage(self, frame):
        qformat = QImage.Format.Format_Indexed8

        if len(frame.shape) == 3:
            if frame.shape[2] == 4:
                qformat = QImage.Format.Format_RGBA8888
            else:
                qformat = QImage.Format.Format_RGB888
        image = QImage(frame, frame.shape[1], frame.shape[0], qformat)
        image = image.rgbSwapped()
        self.ui.videoLabel.setPixmap(QPixmap.fromImage(image))
        #self.ui.videoLabel.setMinimumWidth(frame.shape[1])
        #self.ui.videoLabel.setMinimumHeight(frame.shape[0])
        #self.ui.videoLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)

    def prepare_image(self, image):
        """

        :param image:
        :return:
        """

        height, width, _ = image.shape

        # Створюємо чорне зображення для альфа-каналу
        alpha_channel = np.zeros((height, width), dtype=np.uint8)

        # Створюємо масив, що містить координати пікселів відносно центра зображення
        y_coords, x_coords = np.ogrid[:height, :width]
        center_x, center_y = width // 2, height // 2

        # Обчислюємо градієнт у вигляді еліпса
        a = width / 2
        b = height / 2
        distances = ((x_coords - center_x) / a) ** 2 + ((y_coords - center_y) / b) ** 2
        gradient = 255 * np.sqrt(1 - distances)

        # Застосовуємо градієнт до альфа-каналу
        alpha_channel = np.clip(gradient, 0, 255).astype(np.uint8)

        # Додаємо альфа-канал до оригінального зображення
        image_with_alpha = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        image_with_alpha[:, :, 3] = alpha_channel

        return image_with_alpha
def main():
    argv = sys.argv[1:]
    print(f"argv: {argv}")
    app = QApplication(sys.argv)
    window = FaceLockApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
