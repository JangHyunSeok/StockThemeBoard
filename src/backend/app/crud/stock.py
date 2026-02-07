from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.stock import Stock
from app.schemas.stock import StockCreate


async def get_stocks(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Stock]:
    """종목 목록 조회"""
    result = await db.execute(
        select(Stock).offset(skip).limit(limit).order_by(Stock.name)
    )
    return result.scalars().all()


async def get_stock_by_code(db: AsyncSession, code: str) -> Optional[Stock]:
    """종목코드로 종목 조회"""
    result = await db.execute(
        select(Stock).where(Stock.code == code)
    )
    return result.scalar_one_or_none()


async def create_stock(db: AsyncSession, stock: StockCreate) -> Stock:
    """새 종목 생성"""
    db_stock = Stock(
        code=stock.code,
        name=stock.name,
        market=stock.market,
        market_cap=stock.market_cap
    )
    db.add(db_stock)
    await db.commit()
    await db.refresh(db_stock)
    return db_stock
