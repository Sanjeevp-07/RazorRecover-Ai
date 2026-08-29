import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.db import init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await init_db()

@pytest.mark.asyncio
async def test_full_account_lifecycle():
    transport = ASGITransport(app=app)
    unique_email = f"unique_merchant_{uuid.uuid4().hex[:8]}@example.com"
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Register a new user
        reg_payload = {
            "merchant_name": "Test Company Ltd",
            "email": unique_email,
            "password": "Password123!"
        }
        res_reg = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res_reg.status_code == 201
        data_reg = res_reg.json()
        assert "access_token" in data_reg
        assert data_reg["user"]["email"] == unique_email

        # 2. Attempt duplicate registration with the same email
        res_dup = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res_dup.status_code == 400
        data_dup = res_dup.json()
        assert "already exists" in data_dup["detail"].lower()

        # 3. Login with the created credentials
        login_payload = {
            "email": unique_email,
            "password": "Password123!"
        }
        res_login = await client.post("/api/v1/auth/login", json=login_payload)
        assert res_login.status_code == 200
        data_login = res_login.json()
        assert "access_token" in data_login
        assert data_login["user"]["email"] == unique_email

        # 4. Attempt login with invalid password
        bad_login = {
            "email": unique_email,
            "password": "WrongPassword!"
        }
        res_bad = await client.post("/api/v1/auth/login", json=bad_login)
        assert res_bad.status_code == 401
