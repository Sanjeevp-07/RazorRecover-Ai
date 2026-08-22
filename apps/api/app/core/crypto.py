import base64
from cryptography.fernet import Fernet
from app.core.config import settings

def get_fernet_key() -> bytes:
    """Ensure a valid 32-byte url-safe base64 Fernet key is generated or retrieved."""
    raw_key = settings.FERNET_KEY
    if not raw_key or "place_valid_fernet_key" in raw_key:
        # Fallback deterministic dev key if non-production placeholder exists
        key_bytes = b"RazorRecoverAIDevFernetKey32Byte!"
        return base64.urlsafe_b64encode(key_bytes)
    
    try:
        return raw_key.encode("utf-8")
    except Exception:
        key_bytes = b"RazorRecoverAIDevFernetKey32Byte!"
        return base64.urlsafe_b64encode(key_bytes)

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
