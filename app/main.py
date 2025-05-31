from PyQt5 import QtWidgets
from app.components.MainWindow.MainWindow import FaceLockApp
import sys


def main():
    argv = sys.argv[1:]
    print(f"argv: {argv}")
    app = QtWidgets.QApplication(sys.argv)
    window = FaceLockApp("test.fl")
    window.show()
    window.stream.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
