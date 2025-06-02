import os
import sys

from components.MainWindow.MainWindow import FaceLockApp
from PyQt5 import QtWidgets

os.environ["QT_QPA_PLATFORMTHEME"] = "gtk3"
os.environ["QT_STYLE_OVERRIDE"] = "gtk3"
os.environ["QT_PLUGIN_PATH"] = "/usr/lib/x86_64-linux-gnu/qt5/plugins"


def main():
    """Main function to run the FaceLock application."""
    app = QtWidgets.QApplication(sys.argv)
    print("QtWidgets.QStyleFactory.keys() = ", QtWidgets.QStyleFactory.keys())
    app.setStyle(QtWidgets.QStyleFactory.create("gtk3"))

    argv = sys.argv[1:]

    window = FaceLockApp(argv[0] if argv else None)
    window.show()
    window.stream.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
