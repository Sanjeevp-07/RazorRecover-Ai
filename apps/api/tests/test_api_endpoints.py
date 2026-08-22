import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_all_routes_registered():
    paths = [r.path for r in app.routes if hasattr(r, "path")]
    assert "/health" in paths
    assert len(paths) > 0

@pytest.mark.asyncio
async def test_protected_endpoints_require_bearer_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        assert (await client.get("/api/v1/payments")).status_code == 401
        assert (await client.get("/api/v1/recovery-cases")).status_code == 401
        assert (await client.get("/api/v1/dashboard/summary")).status_code == 401

@pytest.mark.asyncio
async def test_dashboard_summary_with_auth():
    from app.core.security import create_access_token
    import uuid

    demo_user_id = str(uuid.UUID("00000000-0000-0000-0000-000000000002"))
    demo_merchant_id = str(uuid.UUID("00000000-0000-0000-0000-000000000001"))
    token = create_access_token(subject=demo_user_id, merchant_id=demo_merchant_id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()
        assert "failed_revenue_minor" in data
        assert "recoverable_revenue_minor" in data
        assert "recovered_revenue_minor" in data
        assert "recent_cases" in data
        assert len(data["recent_cases"]) > 0
