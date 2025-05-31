from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes


class RsaCryptoProvider:
    """
    A class that provides RSA encryption and decryption functionality.
    """

    def generate_key_pair(self) -> tuple[bytes, bytes]:
        """
        Generates a pair of RSA keys (public and private) in PEM format.

        :return: A tuple (public_key_pem, private_key_pem)
        """
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return public_key_pem, private_key_pem

    def encrypt(self, data: bytes, public_key: bytes) -> bytes:
        """
        Encrypts the given data using the provided public key.

        :param data: The data to encrypt.
        :param public_key: The public key to use for encryption.
        :return: The encrypted data.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    def decrypt(self, encrypted_data: bytes, private_key: bytes) -> bytes:
        """
        Decrypts the given encrypted data using the provided private key.

        :param encrypted_data: The data to decrypt.
        :param private_key: The private key to use for decryption.
        :return: The decrypted data.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    def store_private_key(self, private_key: bytes, file_path: str):
        """
        Stores the private key to a file.

        :param private_key: The private key to store.
        :param file_path: The path to the file where the private key will be stored.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")