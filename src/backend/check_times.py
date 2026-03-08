import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://stockuser:stockpass@postgres:5432/stocktheme"

async def check():
    engine = create_async_engine(DATABASE_URL)
    with open("times_out.txt", "w") as f:
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT id, trade_date, market_type, created_at FROM daily_rankings ORDER BY id DESC LIMIT 5;"))
            rows = res.fetchall()
            for row in rows:
                f.write(f"ID: {row[0]}, Date: {row[1]}, Market: {row[2]}, CreatedAt: {row[3]}\n")
    await engine.dispose()

asyncio.run(check())
