"""
DB 상태 확인 스크립트
market_type 컬럼 존재 여부와 실제 데이터 확인
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from sqlalchemy import text


async def check_db_status():
    """DB 스키마와 데이터 확인"""
    async with AsyncSessionLocal() as session:
        print("=" * 60)
        print("1. daily_rankings 테이블 스키마 확인")
        print("=" * 60)
        
        # 테이블 스키마 확인
        result = await session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'daily_rankings'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        for col in columns:
            print(f"  {col[0]:20} {col[1]:15} NULL:{col[2]:5} DEFAULT:{col[3]}")
        
        # market_type 컬럼 존재 여부
        has_market_type = any(col[0] == 'market_type' for col in columns)
        
        print("\n" + "=" * 60)
        print(f"market_type 컬럼 존재: {'✅ YES' if has_market_type else '❌ NO (마이그레이션 필요!)'}")
        print("=" * 60)
        
        if not has_market_type:
            print("\n⚠️ market_type 컬럼이 없습니다!")
            print("마이그레이션을 실행하세요:")
            print("  docker-compose exec backend alembic upgrade head")
            return
        
        print("\n" + "=" * 60)
        print("2. 2026-02-06 데이터 확인 (삼성전자)")
        print("=" * 60)
        
        # 2/6 삼성전자 데이터 확인
        result = await session.execute(text("""
            SELECT trade_date, stock_code, stock_name, market_type, 
                   current_price, change_rate, trading_value
            FROM daily_rankings
            WHERE trade_date = '2026-02-06'
              AND stock_name LIKE '%삼성전자%'
            ORDER BY market_type, rank
        """))
        
        rows = result.fetchall()
        if rows:
            for row in rows:
                print(f"\n  날짜: {row[0]}")
                print(f"  종목: {row[2]} ({row[1]})")
                print(f"  시장: {row[3]}")
                print(f"  현재가: {row[4]:,}원")
                print(f"  등락률: {row[5]:.2f}%")
                print(f"  거래대금: {row[6]:,}원")
        else:
            print("  ❌ 2026-02-06 삼성전자 데이터가 없습니다.")
        
        print("\n" + "=" * 60)
        print("3. 전체 데이터 통계")
        print("=" * 60)
        
        # 전체 데이터 통계
        result = await session.execute(text("""
            SELECT 
                trade_date,
                market_type,
                COUNT(*) as count
            FROM daily_rankings
            GROUP BY trade_date, market_type
            ORDER BY trade_date DESC, market_type
            LIMIT 10
        """))
        
        stats = result.fetchall()
        if stats:
            print(f"\n  {'날짜':<12} {'시장':<6} {'건수':>6}")
            print("  " + "-" * 30)
            for row in stats:
                print(f"  {row[0]}  {row[1]:<6} {row[2]:>6}개")
        else:
            print("  ❌ 데이터가 없습니다.")


if __name__ == "__main__":
    asyncio.run(check_db_status())
