
import asyncio
from app.scheduler.jobs import fetch_and_save_krx_rankings, fetch_and_save_nxt_rankings

async def run_manual():
    print("🚀 Starting manual trigger for KRX/NXT rankings...")
    await fetch_and_save_krx_rankings()
    await fetch_and_save_nxt_rankings()
    print("✅ Manual trigger completed.")

if __name__ == "__main__":
    asyncio.run(run_manual())
