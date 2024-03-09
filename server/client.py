import socket
import face_recognition
import pickle
import numpy as np

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 9000

class FaceLockClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((SERVER_HOST, SERVER_PORT))

    def send_message(self, message):
        message = pickle.dumps(message)
        print(f"data: {message}")
        self.client.send(message)
        response = self.client.recv(8192)
        if response:
            response = pickle.loads(response)
            if response['status'] == 200:
                print(response)
            else:
                print(response)

    def __del__(self):
        self.client.close

class RegisterUserMessage:
    def __init__(self, username: str, password: str, encode_data: list):
        self.username = username
        self.password = password
        self.encode_data = encode_data.tobytes() # np.frombuffer(encode_data) to convert back
    def __dict__(self):
        return {
            "username": self.username,
            "password": self.password,
            "encode_data": self.encode_data
        }

    def get_action(self):
        return {
            "type": "REGISTER_USER",
            "size": sys.getsizeof(pickle.dumps(self.__dict__()))
        }

    def get_data(self):
        return self.__dict__()

if __name__ == "__main__":
    client = FaceLockClient()
    unknown_image = face_recognition.load_image_file("Biden.png")
    import sys
    biden_encoding = face_recognition.face_encodings(unknown_image)[0]
    print(f"type: {type(biden_encoding)}\n")
    print(f"{sys.getsizeof(pickle.dumps('REGISTER_USER'))}")
    tmp = biden_encoding.tobytes()
    res = np.frombuffer(tmp)
    print(f"test: {res == biden_encoding}\n"
          f"type : {type(res)}")

    message = RegisterUserMessage(
        username="Joe Biden",
        password="12345",
        encode_data=biden_encoding

    )
    data = message.get_data()
    tmp = pickle.dumps(data)
    tmp = pickle.loads(tmp)
    client.send_message(message.get_action())
    client.send_message(message.get_data())
