"""
Profile import/export utilities with encryption support.
"""

import json
import os
import base64
import hashlib
import secrets
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


@dataclass
class ProfileExport:
    """Exported profile data."""
    version: str = "1.0"
    name: str
    use_case: Optional[str] = None
    browser_engine: str = "chromium"
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None
    resolution: str = "1920x1080"
    timezone: Optional[str] = None
    language: Optional[str] = None
    headless: bool = True
    advanced_settings: Optional[str] = None
    fingerprint: Optional[Dict[str, Any]] = None


class ProfileExporter:
    """Export profiles with optional encryption."""

    def __init__(self, encryption_key: Optional[bytes] = None):
        self.encryption_key = encryption_key
        self.fernet = None
        
        if CRYPTO_AVAILABLE and encryption_key:
            self.fernet = Fernet(encryption_key)

    def export_to_dict(
        self,
        profile_data: Dict[str, Any],
        include_fingerprint: bool = True,
        mask_sensitive: bool = True,
    ) -> Dict[str, Any]:
        """Export profile to dictionary."""
        export_data = {
            "version": "1.0",
            "name": profile_data.get("name"),
            "use_case": profile_data.get("use_case"),
            "browser_engine": profile_data.get("browser_engine", "chromium"),
            "user_agent": profile_data.get("user_agent"),
            "proxy": profile_data.get("proxy"),
            "proxy_username": profile_data.get("proxy_username") if not mask_sensitive else None,
            "proxy_password": profile_data.get("proxy_password") if not mask_sensitive else None,
            "resolution": profile_data.get("resolution", "1920x1080"),
            "timezone": profile_data.get("timezone"),
            "language": profile_data.get("language"),
            "headless": profile_data.get("headless", True),
            "advanced_settings": profile_data.get("advanced_settings"),
        }

        if include_fingerprint and profile_data.get("fingerprint"):
            export_data["fingerprint"] = profile_data["fingerprint"]

        return export_data

    def export_to_json(
        self,
        profile_data: Dict[str, Any],
        file_path: Optional[str] = None,
        encrypt: bool = False,
        mask_sensitive: bool = True,
    ) -> str:
        """Export profile to JSON string or file."""
        export_data = self.export_to_dict(profile_data, mask_sensitive=mask_sensitive)
        
        json_data = json.dumps(export_data, indent=2)
        
        if encrypt and self.fernet:
            json_data = self.fernet.encrypt(json_data.encode()).decode()
        
        if file_path:
            Path(file_path).write_text(json_data)
        
        return json_data

    def export_to_base64(
        self,
        profile_data: Dict[str, Any],
        encrypt: bool = False,
    ) -> str:
        """Export profile to base64 encoded string."""
        export_data = self.export_to_dict(profile_data)
        json_data = json.dumps(export_data)
        
        if encrypt and self.fernet:
            json_data = self.fernet.encrypt(json_data.encode()).decode()
        
        return base64.b64encode(json_data.encode()).decode()


class ProfileImporter:
    """Import profiles with decryption support."""

    def __init__(self, encryption_key: Optional[bytes] = None):
        self.encryption_key = encryption_key
        self.fernet = None
        
        if CRYPTO_AVAILABLE and encryption_key:
            self.fernet = Fernet(encryption_key)

    def import_from_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Import profile from dictionary."""
        required_fields = ["name"]
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        return {
            "name": data.get("name"),
            "use_case": data.get("use_case"),
            "browser_engine": data.get("browser_engine", "chromium"),
            "user_agent": data.get("user_agent"),
            "proxy": data.get("proxy"),
            "proxy_username": data.get("proxy_username"),
            "proxy_password": data.get("proxy_password"),
            "resolution": data.get("resolution", "1920x1080"),
            "timezone": data.get("timezone"),
            "language": data.get("language"),
            "headless": data.get("headless", True),
            "advanced_settings": data.get("advanced_settings"),
            "fingerprint": data.get("fingerprint"),
        }

    def import_from_json(
        self,
        json_data: str,
        decrypt: bool = False,
    ) -> Dict[str, Any]:
        """Import profile from JSON string or file."""
        if decrypt and self.fernet:
            json_data = self.fernet.decrypt(json_data.encode()).decode()
        
        data = json.loads(json_data)
        return self.import_from_dict(data)

    def import_from_base64(
        self,
        encoded_data: str,
        decrypt: bool = False,
    ) -> Dict[str, Any]:
        """Import profile from base64 encoded string."""
        json_data = base64.b64decode(encoded_data.encode()).decode()
        return self.import_from_json(json_data, decrypt=decrypt)

    def import_from_file(
        self,
        file_path: str,
        decrypt: bool = False,
    ) -> Dict[str, Any]:
        """Import profile from file."""
        json_data = Path(file_path).read_text()
        return self.import_from_json(json_data, decrypt=decrypt)


def generate_encryption_key(password: str, salt: Optional[bytes] = None) -> tuple[bytes, bytes]:
    """Generate encryption key from password."""
    if not CRYPTO_AVAILABLE:
        raise ImportError("cryptography package not installed")
    
    if salt is None:
        salt = secrets.token_bytes(16)
    
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


def create_profile_export(
    profile_data: Dict[str, Any],
    output_path: str,
    password: Optional[str] = None,
    mask_sensitive: bool = True,
) -> bool:
    """Convenience function to export a profile."""
    try:
        key = None
        if password:
            key, salt = generate_encryption_key(password)
            if output_path.endswith('.encrypted'):
                pass
            elif not output_path.endswith('.json'):
                output_path += '.encrypted'
        elif output_path.endswith('.encrypted'):
            raise ValueError("Password required for encrypted export")

        exporter = ProfileExporter(encryption_key=key)
        exporter.export_to_json(
            profile_data,
            file_path=output_path,
            encrypt=bool(key),
            mask_sensitive=mask_sensitive,
        )
        
        return True
    except Exception as e:
        print(f"Export failed: {e}")
        return False


def create_profile_import(
    input_path: str,
    password: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Convenience function to import a profile."""
    try:
        key = None
        if password:
            key, _ = generate_encryption_key(password)
        
        importer = ProfileImporter(encryption_key=key)
        return importer.import_from_file(
            input_path,
            decrypt=bool(password),
        )
    except Exception as e:
        print(f"Import failed: {e}")
        return None
