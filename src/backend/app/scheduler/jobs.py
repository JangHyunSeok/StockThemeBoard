
"""
스케줄러에서 실행할 작업 정의
"""
import logging
from datetime import datetime

from app.database import AsyncSessionLocal
from app.services.kis_client import get_kis_client
from app.crud import daily_ranking as crud_daily_ranking

from app.core.utils import is_market_open

logger = logging.getLogger(__name__)

async def fetch_and_save_daily_rankings():
    """
    [Job] 일일 거래량 순위 수집 및 저장
    매일 장 마감 후 실행됨 (공휴일 제외)
    """
    # 공휴일 체크
    if not is_market_open():
        logger.info("⛔ [Scheduler] Today is a holiday. Skip job.")
        return

    logger.info("📅 [Scheduler] Daily Ranking Job Started")
    
    # 1. KIS API로 데이터 조회
    try:
        kis_client = await get_kis_client()
        # 토큰 미리 확보
        await kis_client.get_access_token()
        
        # 100위까지 조회
        rankings = await kis_client.get_volume_rank(limit=100)
        
        if not rankings:
            logger.warning("⚠️ [Scheduler] No rankings data fetched. (Holiday or Error?)")
            return
            
        logger.info(f"✅ [Scheduler] Fetched {len(rankings)} items.")
        
    except Exception as e:
        logger.error(f"❌ [Scheduler] Failed to fetch data from KIS: {e}")
        return

    # 2. DB 저장
    async with AsyncSessionLocal() as session:
        try:
            today = datetime.now().date()
            await crud_daily_ranking.save_daily_rankings(session, today, rankings)
            logger.info(f"💾 [Scheduler] Successfully saved rankings for {today}")
        except Exception as e:
            logger.error(f"❌ [Scheduler] Failed to save to DB: {e}")
            await session.rollback()
