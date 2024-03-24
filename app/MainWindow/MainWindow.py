from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QSpacerItem
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(965, 644)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMaximumSize(1024, 1024)
        MainWindow.setContextMenuPolicy(Qt.NoContextMenu)
        MainWindow.setAcceptDrops(True)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet(
            "font: 700 11pt \"Ubuntu Mono\";\n"
            "color: #00062b;\n"
            "background-color: qradialgradient(cx:0.5, cy:0.4, radius: 0.5,\n"
            "                fx:0.5, fy:0.5, stop:0 #00062b,stop:1 #0c004b);\n"
        )

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("")
        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(0, 60, 961, 581)
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setSizeConstraint(QVBoxLayout.SetMaximumSize)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.videoLabel = QLabel(self.verticalLayoutWidget)
        self.videoLabel.setObjectName("videoLabel")
        self.videoLabel.setMinimumSize(854, 480)
        self.videoLabel.setMaximumSize(854, 480)
        self.videoLabel.setBaseSize(200, 200)
        self.videoLabel.setStyleSheet(
            "color: white;\n"
            "font-size: 24px;\n"
            "background-color: none;\n"
            "border: 1px solid #0062d0;\n"
            "border-radius: 50% 50%;"
        )
        self.videoLabel.setScaledContents(True)
        self.videoLabel.setAlignment(Qt.AlignCenter)
        self.verticalLayout.addWidget(self.videoLabel, 0, Qt.AlignHCenter)
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer_2)
        self.pushButton = QPushButton(self.verticalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy1)
        self.pushButton.setMinimumSize(100, 50)
        self.pushButton.setMaximumSize(100, 50)
        self.pushButton.setStyleSheet(
            "color: white;\n"
            "background-color: rgba(0, 0, 0, 30);\n"
            "border: none;\n"
            "border-radius: 10px"
        )
        self.verticalLayout.addWidget(self.pushButton, 0, Qt.AlignHCenter|Qt.AlignVCenter)
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer)
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QApplication.translate("MainWindow", "MainWindow", None))
        self.videoLabel.setText(QApplication.translate("MainWindow", "Loading...", None))
        self.pushButton.setText(QApplication.translate("MainWindow", "Show video", None))
