import asyncio
import sys
import os
import json

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src/backend')))

from app.services.kis_client import get_kis_client

async def test():
    print("Starting KIS indices test with updated logging...")
    try:
        client = await get_kis_client()
        # Test KOSPI
        print("\n--- Testing KOSPI (0001) ---")
        res = await client.get_index_quote("0001")
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        if 'client' in locals():
            await client.close()

if __name__ == "__main__":
    asyncio.run(test())
