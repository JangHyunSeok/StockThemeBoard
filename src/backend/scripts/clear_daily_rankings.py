"""
Daily Rankings 데이터 삭제 스크립트
"""
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.daily_ranking import DailyRanking


# 비동기 세션 생성
engine = create_async_engine(settings.DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def clear_daily_rankings():
    """daily_rankings 테이블의 모든 데이터 삭제"""
    async with async_session() as session:
        print("🗑️  Daily Rankings 데이터 삭제 중...\n")
        
        # 모든 데이터 삭제
        result = await session.execute(delete(DailyRanking))
        await session.commit()
        
        print(f"✅ 삭제 완료! ({result.rowcount}개 행 삭제)\n")


async def main():
    """메인 함수"""
    try:
        await clear_daily_rankings()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
