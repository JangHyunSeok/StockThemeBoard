import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://stockuser:stockpass@localhost:5432/stocktheme"

async def main():
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        result = await conn.execute(text("SHOW timezone;"))
        tz = result.scalar()
        
        result = await conn.execute(text("SELECT NOW();"))
        now = result.scalar()
        
        with open("tz_out.txt", "w") as f:
            f.write(f"Timezone: {tz}\n")
            f.write(f"Now: {now}\n")

if __name__ == "__main__":
    asyncio.run(main())
