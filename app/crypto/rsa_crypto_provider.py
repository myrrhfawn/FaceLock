import hashlib
import os

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


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
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return public_key_pem, private_key_pem

    def encrypt(self, data: bytes, public_key: bytes) -> bytes:
        """
        Hybrid encryption: Encrypts large data using AES, then encrypts AES key with RSA.

        Structure: [RSA_encrypted_AES_key (256 bytes)] + [IV (16 bytes)] + [AES_encrypted_data]

        :param data: The binary data to encrypt.
        :param public_key: RSA public key in PEM format.
        :return: Hybrid encrypted binary data.
        """
        # Generate AES key and IV
        aes_key = os.urandom(32)  # AES-256
        iv = os.urandom(16)

        # AES encryption
        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data) + encryptor.finalize()

        # Encrypt AES key with RSA
        pub_key = serialization.load_pem_public_key(public_key)
        encrypted_aes_key = pub_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        return encrypted_aes_key + iv + encrypted_data

    def decrypt(self, encrypted_payload: bytes, private_key: bytes) -> bytes:
        """
        Hybrid decryption: Decrypts AES key with RSA, then decrypts data with AES.

        :param encrypted_payload: The encrypted payload (RSA_AES_KEY + IV + AES_data)
        :param private_key: RSA private key in PEM format.
        :return: Decrypted original binary data.
        """
        # Extract parts
        rsa_key_len = 256  # RSA 2048-bit = 256 bytes
        iv_len = 16

        encrypted_aes_key = encrypted_payload[:rsa_key_len]
        iv = encrypted_payload[rsa_key_len : rsa_key_len + iv_len]
        encrypted_data = encrypted_payload[rsa_key_len + iv_len :]

        # Decrypt AES key with RSA
        priv_key = serialization.load_pem_private_key(private_key, password=None)
        aes_key = priv_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # AES decryption
        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_data) + decryptor.finalize()
