import os
from typing import Optional

from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class EncryptionManager:

    ARGON2_TIME_COST = 3
    ARGON2_MEMORY_COST = 65536
    ARGON2_PARALLELISM = 4
    ARGON2_HASH_LEN = 32

    SALT_SIZE = 16
    NONCE_SIZE = 12

    def __init__(self):
        self.key: Optional[bytes] = None
        self.salt: Optional[bytes] = None

    def derive_key(self, master_password: str, salt: bytes) -> bytes:
        return hash_secret_raw(
            secret=master_password.encode('utf-8'),
            salt=salt,
            time_cost=self.ARGON2_TIME_COST,
            memory_cost=self.ARGON2_MEMORY_COST,
            parallelism=self.ARGON2_PARALLELISM,
            hash_len=self.ARGON2_HASH_LEN,
            type=Type.ID
        )

    def encrypt(self, plaintext: str) -> bytes:
        if self.key is None or self.salt is None:
            raise ValueError("Encryption key not initialized. Call initialize_new() or initialize_existing() first.")

        nonce = os.urandom(self.NONCE_SIZE)
        aesgcm = AESGCM(self.key)

        ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)

        return self.salt + nonce + ciphertext

    def decrypt(self, encrypted_data: bytes) -> str:
        if self.key is None:
            raise ValueError("Encryption key not initialized.")

        salt = encrypted_data[:self.SALT_SIZE]
        nonce = encrypted_data[self.SALT_SIZE:self.SALT_SIZE + self.NONCE_SIZE]
        ciphertext = encrypted_data[self.SALT_SIZE + self.NONCE_SIZE:]

        aesgcm = AESGCM(self.key)

        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode('utf-8')

    def initialize_new(self, master_password: str) -> None:
        self.salt = os.urandom(self.SALT_SIZE)
        self.key = self.derive_key(master_password, self.salt)

    def initialize_existing(self, master_password: str, encrypted_data: bytes) -> None:
        self.salt = encrypted_data[:self.SALT_SIZE]
        self.key = self.derive_key(master_password, self.salt)

    def verify_password(self, master_password: str, encrypted_data: bytes) -> bool:
        try:
            salt = encrypted_data[:self.SALT_SIZE]
            key = self.derive_key(master_password, salt)

            nonce = encrypted_data[self.SALT_SIZE:self.SALT_SIZE + self.NONCE_SIZE]
            ciphertext = encrypted_data[self.SALT_SIZE + self.NONCE_SIZE:]

            aesgcm = AESGCM(key)
            aesgcm.decrypt(nonce, ciphertext, None)
            return True
        except Exception:
            return False

    def clear(self) -> None:
        self.key = None
        self.salt = None
