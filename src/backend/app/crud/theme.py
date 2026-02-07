from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID

from app.models.theme import Theme
from app.models.theme_stock import ThemeStock
from app.schemas.theme import ThemeCreate


async def get_themes(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Theme]:
    """테마 목록 조회"""
    result = await db.execute(
        select(Theme).offset(skip).limit(limit).order_by(Theme.created_at.desc())
    )
    return result.scalars().all()


async def get_theme_by_id(db: AsyncSession, theme_id: UUID) -> Optional[Theme]:
    """특정 테마 조회 (종목 포함)"""
    result = await db.execute(
        select(Theme)
        .options(selectinload(Theme.theme_stocks))
        .where(Theme.id == theme_id)
    )
    return result.scalar_one_or_none()


async def get_theme_by_name(db: AsyncSession, name: str) -> Optional[Theme]:
    """이름으로 테마 조회"""
    result = await db.execute(
        select(Theme).where(Theme.name == name)
    )
    return result.scalar_one_or_none()


async def create_theme(db: AsyncSession, theme: ThemeCreate) -> Theme:
    """새 테마 생성"""
    db_theme = Theme(
        name=theme.name,
        description=theme.description
    )
    db.add(db_theme)
    await db.commit()
    await db.refresh(db_theme)
    return db_theme
