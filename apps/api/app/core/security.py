from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Dict
import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def create_access_token(subject: str, merchant_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Issue JWT Access Token.
    Per §7.1: JWT payload carries merchant_id and user_id.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode = {
        "sub": subject,
        "merchant_id": merchant_id,
        "exp": expire,
        "type": "access"
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
    return encoded_jwt

def create_refresh_token(subject: str, merchant_id: str) -> str:
    """Issue JWT Refresh Token."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": subject,
        "merchant_id": merchant_id,
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT payload."""
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    return payload
