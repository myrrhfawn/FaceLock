
from PyQt5 import QtWidgets, QtCore
from logging import getLogger
from app.components.RegisterDialog.RegisterDialogUI import Ui_Register
from app.common.frame import Frame
from app.client import FaceLockClient, RegisterUserMessage

logger = getLogger(__name__)
class RegisterDialog(QtWidgets.QDialog):
    def __init__(self, mainWindow, encoding):
        super(RegisterDialog, self).__init__()
        self.mainWindow = mainWindow
        self.encoding = encoding
        self.ui = Ui_Register()
        self.ui.setupUi(self)
        self.logic = 0
        self.value = 1
        self.ui.cancelButton.clicked.connect(self.cancel_button_click)
        self.ui.registerButton.clicked.connect(self.register_button_click)
        self.client = FaceLockClient()

    @QtCore.pyqtSlot()
    def cancel_button_click(self):
        self.mainWindow.show()
        self.close()

    @QtCore.pyqtSlot()
    def register_button_click(self):
        message = RegisterUserMessage(
            username=self.ui.emailInput.text(),
            password=self.ui.emailInput.text(),
            encode_data=self.encoding)
        response = self.client.send_message(message.get_action())
        response = self.client.send_message(message.get_data())

