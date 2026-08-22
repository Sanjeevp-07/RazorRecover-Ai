import pytest
from app.core.crypto import encrypt_secret, decrypt_secret

def test_fernet_encryption_decryption():
    original_secret = "rzp_test_secret_1234567890_abcdef"
    encrypted = encrypt_secret(original_secret)
    
    assert encrypted != original_secret
    assert len(encrypted) > 0
    
    decrypted = decrypt_secret(encrypted)
    assert decrypted == original_secret

def test_fernet_empty_secret_handling():
    assert encrypt_secret("") == ""
    assert decrypt_secret("") == ""
