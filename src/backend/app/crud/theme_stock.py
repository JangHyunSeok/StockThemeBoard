from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
from uuid import UUID

from app.models.theme_stock import ThemeStock
from app.models.theme import Theme
from app.models.stock import Stock


async def get_theme_stock(
    db: AsyncSession, 
    theme_id: UUID, 
    stock_code: str
) -> Optional[ThemeStock]:
    """테마-종목 관계 조회"""
    result = await db.execute(
        select(ThemeStock)
        .where(ThemeStock.theme_id == theme_id)
        .where(ThemeStock.stock_code == stock_code)
    )
    return result.scalar_one_or_none()


async def add_stock_to_theme(
    db: AsyncSession,
    theme_id: UUID,
    stock_code: str,
    weight: int = 5
) -> ThemeStock:
    """테마에 종목 추가"""
    db_theme_stock = ThemeStock(
        theme_id=theme_id,
        stock_code=stock_code,
        weight=weight
    )
    db.add(db_theme_stock)
    await db.commit()
    await db.refresh(db_theme_stock)
    return db_theme_stock


async def update_stock_weight(
    db: AsyncSession,
    theme_id: UUID,
    stock_code: str,
    weight: int
) -> Optional[ThemeStock]:
    """종목 가중치 수정"""
    theme_stock = await get_theme_stock(db, theme_id, stock_code)
    if theme_stock:
        theme_stock.weight = weight
        await db.commit()
        await db.refresh(theme_stock)
    return theme_stock


async def remove_stock_from_theme(
    db: AsyncSession,
    theme_id: UUID,
    stock_code: str
) -> bool:
    """테마에서 종목 제거"""
    result = await db.execute(
        delete(ThemeStock)
        .where(ThemeStock.theme_id == theme_id)
        .where(ThemeStock.stock_code == stock_code)
    )
    await db.commit()
    return result.rowcount > 0
