import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class Encrypter:

    @staticmethod
    def generate_key() -> str:
        return base64.urlsafe_b64encode(AESGCM.generate_key(bit_length=256)).decode()

    def __init__(self):
        key_b64 = os.getenv("SECRETS_ENCRYPTION_KEY")
        if not key_b64:
            raise ValueError("SECRETS_ENCRYPTION_KEY is not set")
        try:
            self._key = base64.urlsafe_b64decode(key_b64)
        except Exception as exc:
            raise ValueError("Key must be URL-safe base64 (44 chars for 32-byte key)") from exc
        if len(self._key) != 32:
            raise ValueError("Key must be 32 raw bytes (256 bits)")
        self._aesgcm = AESGCM(self._key)
    
    def encrypt(self, secret: str) -> str:
        nonce = os.urandom(12)
        ciphertext = self._aesgcm.encrypt(nonce, secret.encode(), None)
        return base64.urlsafe_b64encode(nonce + ciphertext).decode()
    
    def decrypt(self, encrypted_secret: str) -> str:
        encrypted_secret_bytes = base64.urlsafe_b64decode(encrypted_secret)
        nonce = encrypted_secret_bytes[:12]
        ciphertext = encrypted_secret_bytes[12:]
        return self._aesgcm.decrypt(nonce, ciphertext, None).decode()

encrypter = Encrypter()
