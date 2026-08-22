import uuid
from typing import Optional
from pydantic import EmailStr, Field
from app.schemas.base import BaseSchema

class LoginRequest(BaseSchema):
    """Payload for POST /api/v1/auth/login."""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

class RefreshRequest(BaseSchema):
    """Payload for POST /api/v1/auth/refresh."""
    refresh_token: str

class UserResponse(BaseSchema):
    """Authenticated user info."""
    id: uuid.UUID
    merchant_id: uuid.UUID
    email: str
    role: str
    is_active: bool

class TokenResponse(BaseSchema):
    """Token issuance response."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    user: Optional[UserResponse] = None
