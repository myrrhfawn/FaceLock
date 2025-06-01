import hashlib
import os

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

from app.common.User import User


class RsaCryptoProvider:
    """
    A class that provides RSA encryption and decryption functionality.
    """

    def sha256(self, data: bytes) -> str:
        """Compute SHA-256 hash of given data."""
        return hashlib.sha256(data).hexdigest()

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
        :param public_key: The public key in PEM format.
        :return: The encrypted data.
        """
        pub_key = serialization.load_pem_public_key(public_key)

        encrypted = pub_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return encrypted

    def decrypt(self, encrypted_data: bytes, private_key: bytes) -> bytes:
        """
        Decrypts the given encrypted data using the provided private key.

        :param encrypted_data: The encrypted data.
        :param private_key: The private key in PEM format.
        :return: The decrypted data.
        """
        priv_key = serialization.load_pem_private_key(private_key, password=None)

        decrypted = priv_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return decrypted
