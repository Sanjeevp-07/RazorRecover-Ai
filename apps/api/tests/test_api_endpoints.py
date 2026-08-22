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
