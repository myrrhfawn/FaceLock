import sys

from components.MainWindow.MainWindow import FaceLockApp
from PyQt5 import QtWidgets


def main():
    """Main function to run the FaceLock application."""
    app = QtWidgets.QApplication(sys.argv)
    argv = sys.argv[1:]

    window = FaceLockApp(argv[0] if argv else None)
    window.show()
    window.stream.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
