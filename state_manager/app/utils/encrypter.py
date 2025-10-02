import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Encrypter:
    @staticmethod
    def generate_key() -> str:
        """Generate a new 256-bit key encoded in URL-safe base64 (44 chars)."""
        return base64.urlsafe_b64encode(AESGCM.generate_key(bit_length=256)).decode()

    def __init__(self, key_b64: str = None):
        """
        Initialize Encrypter with a 32-byte URL-safe base64 key.

        Args:
            key_b64 (str, optional): Base64 key. If not provided, it is read from ENCRYPTION_KEY env var.

        Raises:
            ValueError: If key is missing, invalid, or not 32 bytes.
        """
        if key_b64 is None:
            key_b64 = os.getenv("ENCRYPTION_KEY")

        if not key_b64:
            raise ValueError("ENCRYPTION_KEY environment variable is not set.")

        try:
            self._key = base64.urlsafe_b64decode(key_b64)
        except Exception as exc:
            raise ValueError(
                "Key must be URL-safe base64 (44 chars for 32-byte key)"
            ) from exc

        if len(self._key) != 32:
            raise ValueError("Key must be 32 raw bytes (256 bits)")

        self._aesgcm = AESGCM(self._key)

    def encrypt(self, secret: str) -> str:
        nonce = os.urandom(12)
        ciphertext = self._aesgcm.encrypt(nonce, secret.encode(), None)
        return base64.urlsafe_b64encode(nonce + ciphertext).decode()

    def decrypt(self, encrypted_secret: str) -> str:
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_secret)
        nonce = encrypted_bytes[:12]
        ciphertext = encrypted_bytes[12:]
        return self._aesgcm.decrypt(nonce, ciphertext, None).decode()


# Singleton instance
_encrypter_instance = None

def get_encrypter() -> Encrypter:
    """Return a singleton Encrypter instance."""
    global _encrypter_instance
    if _encrypter_instance is None:
        _encrypter_instance = Encrypter()
    return _encrypter_instance
