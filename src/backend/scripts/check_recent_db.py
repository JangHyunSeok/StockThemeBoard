
import asyncio
from app.database import AsyncSessionLocal
from app.models.daily_ranking import DailyRanking
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as session:
        # Get latest 5 distinct trade dates
        res = await session.execute(
            select(DailyRanking.trade_date, DailyRanking.market_type)
            .distinct()
            .order_by(DailyRanking.trade_date.desc())
            .limit(10)
        )
        data = res.all()
        print("Recent Daily Rankings (Date, Market):")
        for row in data:
            print(f"- {row[0]}, {row[1]}")

if __name__ == "__main__":
    asyncio.run(check())
