import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.db import init_db
from app.services.auth_service import AuthService

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await init_db()

@pytest.mark.asyncio
async def test_backtest_simulation_api():
    transport = ASGITransport(app=app)
    unique_email = f"sim_user_{uuid.uuid4().hex[:8]}@example.com"
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Register test merchant user
        reg_payload = {
            "merchant_name": "Simulation Test Merchant",
            "email": unique_email,
            "password": "Password123!"
        }
        res_reg = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res_reg.status_code == 201
        token = res_reg.json()["access_token"]

        # 2. Trigger backtest simulation API
        sim_payload = {
            "dataset": [
                {
                    "provider_payment_id": "pay_test_001",
                    "error_code": "OTP_3DS_ABANDONED",
                    "error_description": "User left OTP page",
                    "amount_minor": 500000,
                    "customer_history_score": 0.85,
                    "retry_count": 1,
                    "method": "card"
                },
                {
                    "provider_payment_id": "pay_test_002",
                    "error_code": "ISSUER_RISK_DECLINE",
                    "error_description": "Suspected velocity card testing",
                    "amount_minor": 150000,
                    "customer_history_score": 0.10,
                    "retry_count": 5,
                    "velocity_flag": True,
                    "method": "card"
                }
            ],
            "parameters": {
                "model": "meta/llama-3.1-70b-instruct"
            }
        }

        headers = {"Authorization": f"Bearer {token}"}
        res_sim = await client.post("/api/v1/backtests", json=sim_payload, headers=headers)
        assert res_sim.status_code == 201
        sim_data = res_sim.json()

        assert sim_data["total_dataset_cases"] == 2
        assert "simulated_recovery_rate" in sim_data
        assert "projected_roi_multiplier" in sim_data
        assert sim_data["status"] == "COMPLETED"

        # 3. Retrieve backtest results by ID
        backtest_id = sim_data["id"]
        res_get = await client.get(f"/api/v1/backtests/{backtest_id}", headers=headers)
        assert res_get.status_code == 200
        get_data = res_get.json()
        assert get_data["id"] == backtest_id
