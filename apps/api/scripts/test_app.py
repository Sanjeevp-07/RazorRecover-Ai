import asyncio
import httpx
from app.main import app

async def main():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.get("/health")
        print("\n--- APP VERIFICATION RUN ---")
        print(f"Status Code: {res.status_code}")
        print(f"Response Payload: {res.json()}")
        
        openapi_res = await client.get("/api/v1/openapi.json")
        print(f"OpenAPI Spec Status Code: {openapi_res.status_code}")
        print(f"API Title: {openapi_res.json()['info']['title']}")
        print(f"API Version: {openapi_res.json()['info']['version']}")
        print("----------------------------\n")

if __name__ == "__main__":
    asyncio.run(main())
