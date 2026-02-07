"""
일일 거래량 순위 CRUD
"""
from datetime import date
from typing import List, Dict, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_ranking import DailyRanking


async def save_daily_rankings(
    db: AsyncSession,
    trade_date: date,
    rankings: List[Dict]
) -> None:
    """일일 거래량 순위 저장 (기존 데이터 삭제 후 새로 저장)
    
    Args:
        db: 데이터베이스 세션
        trade_date: 거래일
        rankings: 순위 데이터 리스트
    """
    # 기존 데이터 삭제 (동일 날짜)
    await db.execute(
        delete(DailyRanking).where(DailyRanking.trade_date == trade_date)
    )
    
    # 새 데이터 삽입
    for ranking in rankings:
        daily_ranking = DailyRanking(
            trade_date=trade_date,
            stock_code=ranking["code"],
            stock_name=ranking["name"],
            rank=ranking["rank"],
            current_price=ranking["current_price"],
            change_price=ranking["change_price"],
            change_rate=ranking["change_rate"],
            volume=ranking["volume"],
            trading_value=ranking["trading_value"],
        )
        db.add(daily_ranking)
    
    await db.commit()


async def get_rankings_by_date(
    db: AsyncSession,
    trade_date: date
) -> List[Dict]:
    """특정 날짜의 거래량 순위 조회
    
    Args:
        db: 데이터베이스 세션
        trade_date: 거래일
    
    Returns:
        List[Dict]: 순위 데이터 리스트
    """
    result = await db.execute(
        select(DailyRanking)
        .where(DailyRanking.trade_date == trade_date)
        .order_by(DailyRanking.rank)
    )
    rankings = result.scalars().all()
    
    return [
        {
            "code": r.stock_code,
            "name": r.stock_name,
            "rank": r.rank,
            "current_price": r.current_price,
            "change_price": r.change_price,
            "change_rate": r.change_rate,
            "volume": r.volume,
            "trading_value": r.trading_value,
        }
        for r in rankings
    ]


async def get_latest_ranking_date(db: AsyncSession) -> Optional[date]:
    """가장 최근 거래량 순위 데이터의 날짜 조회
    
    Args:
        db: 데이터베이스 세션
    
    Returns:
        Optional[date]: 가장 최근 거래일 (데이터 없으면 None)
    """
    result = await db.execute(
        select(DailyRanking.trade_date)
        .distinct()
        .order_by(DailyRanking.trade_date.desc())
        .limit(1)
    )
    latest_date = result.scalar_one_or_none()
    return latest_date
