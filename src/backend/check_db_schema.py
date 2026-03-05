import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

DATABASE_URL = "postgresql+asyncpg://stockuser:stockpass@postgres:5432/stocktheme"

async def check():
    engine = create_async_engine(DATABASE_URL)
    with open("schema_out.txt", "w") as f:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT column_default FROM information_schema.columns WHERE table_name = 'daily_rankings' AND column_name = 'created_at';"))
            default_val = result.scalar()
            f.write(f"DEFAULT INFO: {default_val}\n")
            
            res_time = await conn.execute(text("SELECT now();"))
            f.write(f"DB NOW: {res_time.scalar()}\n")
            
            # Check actual records
            res_records = await conn.execute(text("SELECT created_at FROM daily_rankings ORDER BY id DESC LIMIT 1;"))
            f.write(f"LATEST RECORD created_at: {res_records.scalar()}\n")
            
    await engine.dispose()

asyncio.run(check())
