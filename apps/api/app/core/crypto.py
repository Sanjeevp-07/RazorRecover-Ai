import base64
from cryptography.fernet import Fernet
from app.core.config import settings

# Fallback deterministic dev Fernet key (32 bytes base64 encoded)
DEV_FERNET_KEY = b"z6eX8N7q2D8V5xQ4m7L9K2j5H8P1w3R6A7B8C9D0E1F="

def get_fernet_key() -> bytes:
    """Ensure a valid 32-byte url-safe base64 Fernet key is generated or retrieved."""
    raw_key = settings.FERNET_KEY
    if not raw_key or "place_valid_fernet_key" in raw_key:
        return DEV_FERNET_KEY
    
    try:
        key_bytes = raw_key.encode("utf-8")
        # Validate Fernet key
        Fernet(key_bytes)
        return key_bytes
    except Exception:
        return DEV_FERNET_KEY

def encrypt_secret(plain_text: str) -> str:
    """Encrypt a sensitive string (e.g. Razorpay Key/Webhook Secret) at rest using Fernet."""
    if not plain_text:
        return ""
    fernet = Fernet(get_fernet_key())
    return fernet.encrypt(plain_text.encode("utf-8")).decode("utf-8")

def decrypt_secret(cipher_text: str) -> str:
    """Decrypt a Fernet encrypted secret string."""
    if not cipher_text:
        return ""
    fernet = Fernet(get_fernet_key())
    return fernet.decrypt(cipher_text.encode("utf-8")).decode("utf-8")
