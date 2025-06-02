from logging import getLogger

from common.client import FaceLockClient, RegisterUserMessage
from common.constants import DEBUG
from common.user import User
from components.RegisterDialog.RegisterDialogUI import Ui_Register
from crypto.rsa_crypto_provider import RsaCryptoProvider
from PyQt5 import QtCore, QtWidgets

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
        self.rsa_provider = RsaCryptoProvider()
        self.user = None

    @QtCore.pyqtSlot()
    def cancel_button_click(self):
        """Handle cancel button click."""
        self.mainWindow.show()
        self.close()

    @QtCore.pyqtSlot()
    def register_button_click(self):
        """Handle register button click."""
        client = FaceLockClient()
        public_key, private_key = self.rsa_provider.generate_key_pair()
        message = RegisterUserMessage(
            username=self.ui.emailInput.text(),
            password=self.ui.passInput.text(),
            encode_data=self.encoding,
            public_key=public_key,
        )
        print(f"Registering user with username: {self.encoding}")
        response = client.send_message(message)
        user_data = client.get_data(response)

        self.user = User(**user_data)
        self.user.store_private_key(private_key)
        if DEBUG:
            self.ui.debug_label.setText("Register success")
        if response and response["status"] == 200:
            self.mainWindow.ui.debug_label.setText("Register successfully.")
            self.mainWindow.stream.video_stream.set_reload_true()
            self.mainWindow.show()
            self.close()
        else:
            self.ui.debug_label.setText("Failed to register user. Try again")


def store_private_key(private_key, user):
    """
    Store the private key securely.
    This is a placeholder function. Implement secure storage as needed.
    """
    with open("private_key.pem", "wb") as f:
        f.write(private_key)
