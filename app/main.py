import sys
import time

from PySide6.QtWidgets import QApplication, QMainWindow

from MainWindow.MainWindow2 import Ui_MainWindow
class FaceLockApp(QMainWindow):
    def __init__(self):
        super(FaceLockApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def change_label_text(self, text):
        self.ui.label.setText(text)
def main():
    argv = sys.argv[1:]
    print(f"argv: {argv}")
    app = QApplication(sys.argv)
    window = FaceLockApp()
    window.show()
    time.sleep(1)
    window.change_label_text(str(argv))
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

