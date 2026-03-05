import asyncio
from httpx import AsyncClient

async def test_api():
    async with AsyncClient() as client:
        # FastAPI 서버가 떠있다고 가정 (보통 8000포트)
        try:
            resp = await client.get("http://localhost:8000/api/v1/rankings/volume-rank-by-theme?market=ALL")
            print("Status:", resp.status_code)
            data = resp.json()
            if isinstance(data, dict) and data:
                print("Data keys length:", len(data))
                for k, v in data.items():
                    print(f"Sector {k}: {len(v)} items")
            else:
                print("Data:", data)
        except Exception as e:
            print("Request failed:", e)

if __name__ == "__main__":
    asyncio.run(test_api())
