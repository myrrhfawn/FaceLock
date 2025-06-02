import logging
import os

from common.constants import KEY_STORAGE_PATH

logger = logging.getLogger(__name__)


class User:
    def __init__(self, user_id, username, encode_data, public_key, **kwargs):
        self.user_id = user_id
        self.username = username
        self.encode_data = encode_data
        self.public_key: bytes = public_key

    def to_dict(self):
        """"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "encode_data": self.encode_data,
            "public_key": self.public_key,
        }

    def __repr__(self):
        return f"User(id={self.user_id}, username={self.username})"

    def get_private_key_path(self):
        """
        Returns the path to the user's private key file.

        :return: The path to the private key file.
        """
        keys_folder = os.path.join(KEY_STORAGE_PATH)
        if not os.path.exists(keys_folder):
            os.makedirs(keys_folder)
        return os.path.join(
            keys_folder, f"{self.username}_id_{self.user_id}_private_key.pem"
        )

    def store_private_key(self, private_key: bytes):
        """
        Stores the private key to a file.

        :param private_key: The private key to store.
        """
        with open(self.get_private_key_path(), "wb") as f:
            f.write(private_key)

    def load_private_key(self):
        """
        Loads the private key from the file.

        :return: The private key as bytes.
        """
        file_path = self.get_private_key_path()
        if not os.path.exists(file_path):
            logger.info(
                f"Private key file does not exist at {file_path}. Returning None."
            )
            return None
        try:
            with open(file_path, "rb") as f:
                private_key_bytes = f.read()
            return private_key_bytes
        except Exception as e:
            logger.exception(f"Failed to load private key from {file_path}: {e}")
            return None
