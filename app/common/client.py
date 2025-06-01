import logging
import pickle
import socket
import sys

from common.constants import SERVER_HOST, SERVER_PORT

logger = logging.getLogger(__name__)


class FaceLockClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((SERVER_HOST, SERVER_PORT))

    def send_message(self, message):
        """Sends a message to the server and handles the response."""
        # Send action
        action = message.get_action()
        logger.info(f"Sending action to server: {action['type']}")
        response = self._send(action)
        if action["size"] > 38:
            # If size is greater than 38, we expect data to follow
            if response["status"] != 200:
                logger.error(f"Failed to send action: {action}")
                return response
            data = message.get_data()
            logger.info("Sending data to server")
            return self._send(data)
        return response

    def _send(self, data):
        """Sends data to the server."""
        data = pickle.dumps(data)
        self.client.send(data)
        data = self.client.recv(8192)
        return pickle.loads(data)

    def get_data(self, response):
        """Receives data from the server based on the response."""
        buffer_size = response["size"] if response.get("size") else 8192
        logger.info(f"Receiving data from server with buffer size: {buffer_size}")
        data = self.client.recv(buffer_size)

        if not data:
            logger.error("No data received from server.")
            return None
        data = pickle.loads(data)
        data["status"] = response.get("status", 500)
        return data

    def __del__(self):
        self.client.close()


class Message:
    def __init__(self, request_type, action_type):
        self.request_type = request_type
        self.action_type = action_type

    def get_action(self):
        """Returns the action details for the message."""
        return {
            "request": self.request_type,
            "type": self.action_type,
            "size": sys.getsizeof(pickle.dumps(self.__dict__())),
        }

    def get_data(self):
        """Returns the data to be sent with the message."""
        return self.__dict__()


class RegisterUserMessage(Message):
    def __init__(
        self, username: str, password: str, encode_data: list, public_key: bytes
    ):
        """Initializes a message for registering a user."""
        super().__init__("POST", "REGISTER_USER")
        self.username = username
        self.password = password
        self.encode_data = (
            encode_data.tobytes()
        )  # np.frombuffer(encode_data) to convert back
        self.public_key = public_key

    def __dict__(self):
        return {
            "username": self.username,
            "password": self.password,
            "encode_data": self.encode_data,
            "public_key": self.public_key,
        }


class GetEncodingsMessage(Message):
    def __init__(self):
        super().__init__("GET", "GET_ENCODINGS")

    def __dict__(self):
        return {}


class GetUserMessage(Message):
    def __init__(self, username: str):
        """Initializes a message for getting user data."""
        super().__init__("GET", "GET_USER")
        self.username = username

    def __dict__(self):
        return {"username": self.username}
