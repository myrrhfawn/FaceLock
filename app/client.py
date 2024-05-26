import socket
import face_recognition
import pickle

import logging
import numpy as np
import sys
from app.constants import SERVER_HOST, SERVER_PORT

logger = logging.getLogger(__name__)
class FaceLockClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((SERVER_HOST, SERVER_PORT))

    def send_message(self, message):
        message = pickle.dumps(message)
        self.client.send(message)
        response = self.client.recv(8192)
        if response:
            response = pickle.loads(response)
            if response['status'] == 200:
                return response
            else:
                return response

    def get_data(self, response):
        buffer_size = response['size'] if response.get('size') else 8192
        data = self.client.recv(buffer_size)
        return pickle.loads(data)

    def __del__(self):
        self.client.close


class Message:
    def __init__(self, request_type, action_type):
        self.request_type = request_type
        self.action_type = action_type

    def get_action(self):
        return {
            "request": self.request_type,
            "type": self.action_type,
            "size": sys.getsizeof(pickle.dumps(self.__dict__()))
        }

    def get_data(self):
        return self.__dict__()

class RegisterUserMessage(Message):
    def __init__(self, username: str, password: str, encode_data: list):
        super().__init__("POST", "REGISTER_USER")
        self.username = username
        self.password = password
        self.encode_data = encode_data.tobytes() # np.frombuffer(encode_data) to convert back

    def __dict__(self):
        return {
            "username": self.username,
            "password": self.password,
            "encode_data": self.encode_data
        }


class GetEncodingsMessage(Message):
    def __init__(self):
        super().__init__("GET", "GET_ENCODINGS")

    def __dict__(self):
        return {}
