import sys
from PySide6.QtWidgets import QApplication, QMainWindow

from MainWindow.MainWindow import Ui_MainWindow

class FaceLockApp(QMainWindow):
    def __init__(self):
        super(FaceLockApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceLockApp()
    window.show()
    sys.exit(app.exec())
