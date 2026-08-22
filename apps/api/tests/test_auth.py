import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token

def test_password_hashing():
    plain_pw = "SuperSecurePassword123!"
    hashed = get_password_hash(plain_pw)
    
    assert verify_password(plain_pw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_access_and_refresh_token_lifecycle():
    user_id = str(uuid.uuid4())
    merchant_id = str(uuid.uuid4())
    
    access_token = create_access_token(subject=user_id, merchant_id=merchant_id)
    refresh_token = create_refresh_token(subject=user_id, merchant_id=merchant_id)
    
    access_payload = decode_token(access_token)
    assert access_payload["sub"] == user_id
    assert access_payload["merchant_id"] == merchant_id
    assert access_payload["type"] == "access"
    
    refresh_payload = decode_token(refresh_token)
    assert refresh_payload["sub"] == user_id
    assert refresh_payload["merchant_id"] == merchant_id
    assert refresh_payload["type"] == "refresh"

@pytest.mark.asyncio
async def test_auth_me_requires_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 403  # Forbidden without Authorization header

@pytest.mark.asyncio
async def test_auth_login_extra_fields_forbidden():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Pydantic extra="forbid" test
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@merchant.com",
            "password": "password123",
            "extra_unallowed_field": "hacker"
        })
        assert response.status_code == 422  # Validation error due to extra="forbid"
