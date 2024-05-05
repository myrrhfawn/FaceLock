# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QLayout, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(965, 644)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMaximumSize(QSize(1024, 1024))
        MainWindow.setContextMenuPolicy(Qt.NoContextMenu)
        MainWindow.setAcceptDrops(True)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet(u"font: 700 11pt \"Ubuntu Mono\";\n"
"color: #00062b;\n"
"background-color: qradialgradient(cx:0.5, cy:0.4, radius: 0.5,\n"
"                fx:0.5, fy:0.5, stop:0 #00062b,stop:1 #0c004b);\n"
"\n"
"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"")
        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 60, 961, 581))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetMaximumSize)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.videoLabel = QLabel(self.verticalLayoutWidget)
        self.videoLabel.setObjectName(u"videoLabel")
        self.videoLabel.setMinimumSize(QSize(854, 480))
        self.videoLabel.setMaximumSize(QSize(854, 480))
        self.videoLabel.setBaseSize(QSize(200, 200))
        self.videoLabel.setStyleSheet(u"color: white;\n"
"font-size: 24px;\n"
"background-color: none;\n"
"border: 1px solid #0062d0;\n"
"border-radius: 50% 50%;")
        self.videoLabel.setScaledContents(True)
        self.videoLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.videoLabel, 0, Qt.AlignHCenter)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.pushButton = QPushButton(self.verticalLayoutWidget)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy1)
        self.pushButton.setMinimumSize(QSize(100, 50))
        self.pushButton.setMaximumSize(QSize(100, 50))
        self.pushButton.setStyleSheet(u"color: white;\n"
"background-color: rgba(0, 0, 0, 30);\n"
"border: none;\n"
"border-radius: 10px")

        self.verticalLayout.addWidget(self.pushButton, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.videoLabel.setText(QCoreApplication.translate("MainWindow", u"Loading...", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Show video", None))
    # retranslateUi

