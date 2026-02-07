"""
Daily Rankings 초기 데이터 생성 스크립트

stocks 테이블의 종목들을 기준으로 daily_rankings 테이블에 초기 데이터를 생성합니다.
"""
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from datetime import date, datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.stock import Stock
from app.models.daily_ranking import DailyRanking
import random


# 비동기 세션 생성
engine = create_async_engine(settings.DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed_daily_rankings():
    """stocks 테이블 기반으로 daily_rankings 초기 데이터 생성"""
    async with async_session() as session:
        print("🌱 Daily Rankings 초기 데이터 생성 시작...\n")
        
        # 1. stocks 테이블에서 모든 종목 조회
        print("📈 종목 목록 조회 중...")
        result = await session.execute(select(Stock))
        stocks = result.scalars().all()
        
        if not stocks:
            print("❌ stocks 테이블에 데이터가 없습니다!")
            print("   먼저 'python scripts/seed_data.py'를 실행해주세요.")
            return
        
        print(f"  ✅ {len(stocks)}개 종목 발견\n")
        
        # 2. 오늘 날짜 기준으로 daily_rankings 데이터 생성
        today = datetime.now().date()
        print(f"📅 데이터 생성 날짜: {today}\n")
        
        print("💾 Daily Rankings 데이터 생성 중...")
        
        for idx, stock in enumerate(stocks, start=1):
            # 더미 데이터 생성 (실제 시세 데이터처럼 보이도록)
            base_price = random.randint(10000, 100000)
            change_rate = random.uniform(-5.0, 5.0)
            change_price = int(base_price * change_rate / 100)
            current_price = base_price + change_price
            volume = random.randint(1000000, 50000000)
            trading_value = current_price * volume
            
            daily_ranking = DailyRanking(
                trade_date=today,
                stock_code=stock.code,
                stock_name=stock.name,
                rank=idx,
                current_price=current_price,
                change_price=change_price,
                change_rate=round(change_rate, 2),
                volume=volume,
                trading_value=trading_value,
            )
            session.add(daily_ranking)
            
            print(f"  ✅ [{idx:2d}] {stock.name:15s} | "
                  f"현재가: {current_price:>8,}원 | "
                  f"등락률: {change_rate:>6.2f}% | "
                  f"거래대금: {trading_value//100000000:>6,}억")
        
        await session.commit()
        
        print("\n" + "=" * 80)
        print("🎉 Daily Rankings 초기 데이터 생성 완료!")
        print("=" * 80)
        print(f"\n📊 생성된 데이터:")
        print(f"  - 날짜: {today}")
        print(f"  - 종목 수: {len(stocks)}개")
        print(f"\n✨ 이제 API를 통해 거래량 순위를 조회할 수 있습니다!")
        print(f"   👉 http://localhost:8000/api/v1/rankings/volume-rank-by-theme\n")


async def main():
    """메인 함수"""
    try:
        await seed_daily_rankings()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
