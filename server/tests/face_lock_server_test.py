import unittest
import pickle
import face_recognition
from unittest.mock import patch
from client import FaceLockClient, RegisterUserMessage, SERVER_HOST, SERVER_PORT


class TestFaceLockServer(unittest.TestCase):
    def test_register_user(self):
        client = FaceLockClient()
        return_value = {"status": 200, "message": "SUCCESS"}
        unknown_image = face_recognition.load_image_file("Biden.png")
        biden_encoding = face_recognition.face_encodings(unknown_image)[0]
        message = RegisterUserMessage(
            username="Joe Biden", password="12345", encode_data=biden_encoding
        )

        # Act
        response = client.send_message(message)
        self.assertDictEqual(response, return_value)


if __name__ == "__main__":
    unittest.main()
