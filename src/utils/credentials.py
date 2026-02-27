"""
Credentials encryption utilities.
Provides secure storage for passwords and sensitive data.
"""

import os
import base64
import hashlib
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

try:
    import bcrypt

    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False


class CredentialsManager:
    """Manage encrypted credentials for proxy and admin passwords."""

    def __init__(self, encryption_key: Optional[bytes] = None):
        if encryption_key is None:
            encryption_key = os.environ.get("ENCRYPTION_KEY", "").encode()
            if not encryption_key:
                encryption_key = self._generate_key()

        self.cipher = Fernet(encryption_key)

    def _generate_key(self) -> bytes:
        """Generate a new encryption key."""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"default_key_change_in_production"))
        return key

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string."""
        encrypted = self.cipher.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a ciphertext string."""
        try:
            decoded = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception:
            return ciphertext

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        if not BCRYPT_AVAILABLE:
            return password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against a bcrypt hash."""
        if not BCRYPT_AVAILABLE:
            return password == hashed
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except Exception:
            return False


credentials_manager = CredentialsManager()
