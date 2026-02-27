"""
SSL/TLS configuration module.
Provides SSL certificate generation and management for production deployment.
"""

import os
import ssl
import logging
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SSLConfig:
    """SSL configuration."""
    cert_file: str
    key_file: str
    enabled: bool = False


def generate_self_signed_cert(
    cert_path: str = "certs/server.crt",
    key_path: str = "certs/server.key",
    days_valid: int = 365,
    host: str = "localhost",
) -> Tuple[str, str]:
    """
    Generate self-signed SSL certificate for development/testing.
    
    Args:
        cert_path: Path to save certificate
        key_path: Path to save private key
        days_valid: Days until certificate expires
        host: Hostname for certificate
        
    Returns:
        Tuple of (cert_path, key_path)
    """
    cert_dir = Path(cert_path).parent
    cert_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import datetime
        
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Development"),
            x509.NameAttribute(NameOID.COMMON_NAME, host),
        ])
        
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=days_valid))
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.DNSName(host),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]),
                critical=False,
            )
            .sign(key, hashes.SHA256(), default_backend())
        )
        
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open(key_path, "wb") as f:
            f.write(
                key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
        
        logger.info(f"Self-signed certificate generated: {cert_path}")
        return cert_path, key_path
        
    except ImportError:
        logger.warning("cryptography not installed, using openssl command")
        return _generate_cert_openssl(cert_path, key_path, days_valid, host)


def _generate_cert_openssl(
    cert_path: str,
    key_path: str,
    days_valid: int,
    host: str,
) -> Tuple[str, str]:
    """Generate certificate using openssl command."""
    import subprocess
    
    cert_dir = Path(cert_path).parent
    cert_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "openssl", "req", "-x509",
        "-newkey", "rsa:2048",
        "-keyout", key_path,
        "-out", cert_path,
        "-days", str(days_valid),
        "-nodes",
        "-subj", f"/C=US/ST=CA/L=San Francisco/O=Development/CN={host}",
        "-addext", f"subjectAltName=DNS:{host},DNS:localhost,IP:127.0.0.1",
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"Self-signed certificate generated: {cert_path}")
        return cert_path, key_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate certificate: {e}")
        raise


def load_ssl_config(
    cert_file: Optional[str] = None,
    key_file: Optional[str] = None,
) -> SSLConfig:
    """
    Load SSL configuration from environment or files.
    
    Environment variables:
        SSL_CERT: Path to certificate file
        SSL_KEY: Path to private key file
        SSL_ENABLED: Enable SSL (true/false)
        SSL_GENERATE: Auto-generate self-signed cert (true/false)
    """
    cert_file = cert_file or os.environ.get("SSL_CERT", "certs/server.crt")
    key_file = key_file or os.environ.get("SSL_KEY", "certs/server.key")
    enabled = os.environ.get("SSL_ENABLED", "false").lower() == "true"
    auto_generate = os.environ.get("SSL_GENERATE", "false").lower() == "true"
    
    if enabled:
        cert_path = Path(cert_file)
        key_path = Path(key_file)
        
        if auto_generate or not (cert_path.exists() and key_path.exists()):
            if auto_generate:
                logger.info("Auto-generating SSL certificate")
                generate_self_signed_cert(cert_file, key_file)
            else:
                logger.warning(
                    f"SSL enabled but cert ({cert_file}) or key ({key_file}) not found. "
                    "Set SSL_GENERATE=true to auto-generate."
                )
                enabled = False
        else:
            logger.info(f"SSL enabled with cert: {cert_file}")
    
    return SSLConfig(
        cert_file=cert_file,
        key_file=key_file,
        enabled=enabled,
    )


def create_ssl_context(ssl_config: SSLConfig) -> Optional[ssl.SSLContext]:
    """Create SSL context for uvicorn/FastAPI."""
    if not ssl_config.enabled:
        return None
    
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(ssl_config.cert_file, ssl_config.key_file)
    
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    
    ssl_context.set_ciphers("ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS")
    
    return ssl_context


import ipaddress
