
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


async def fetch_and_save_krx_rankings():
    """
    [Job] KRX 정규장 일일 거래량 순위 수집 및 저장
    매일 장 마감 후 실행됨 (15:40, 공휴일 제외)
    """
    # 공휴일 체크
    if not is_market_open():
        logger.info("⛔ [Scheduler] Today is a holiday. Skip KRX job.")
        return

    logger.info("📅 [Scheduler] KRX Daily Ranking Job Started")
    
    # 1. KIS API로 데이터 조회
    try:
        kis_client = await get_kis_client()
        
        # KIS API 최대 30건 지원 (페이징 미지원)
        rankings = await kis_client.get_volume_rank(limit=30, market="J")
        
        if not rankings:
            logger.warning("⚠️ [Scheduler] No KRX rankings data fetched.")
            return
            
        logger.info(f"✅ [Scheduler] Fetched {len(rankings)} KRX items.")
        
    except Exception as e:
        logger.error(f"❌ [Scheduler] Failed to fetch KRX data from KIS: {e}")
        return

    # 2. DB 저장 (market_type="KRX")
    async with AsyncSessionLocal() as session:
        try:
            today = datetime.now().date()
            await crud_daily_ranking.save_daily_rankings(session, today, rankings, market_type="KRX")
            logger.info(f"💾 [Scheduler] Successfully saved KRX rankings for {today}")
        except Exception as e:
            logger.error(f"❌ [Scheduler] Failed to save KRX data to DB: {e}")
            await session.rollback()


async def fetch_and_save_nxt_rankings():
    """
    [Job] NXT 야간거래 일일 거래량 순위 수집 및 저장
    매일 야간거래 마감 후 실행됨 (20:00, 공휴일 제외)
    """
    # 공휴일 체크
    if not is_market_open():
        logger.info("⛔ [Scheduler] Today is a holiday. Skip NXT job.")
        return

    logger.info("📅 [Scheduler] NXT Daily Ranking Job Started")
    
    # 1. KIS API로 데이터 조회
    try:
        kis_client = await get_kis_client()
        
        # KIS API 최대 30건 지원 (페이징 미지원)
        rankings = await kis_client.get_volume_rank(limit=30, market="NX")
        
        if not rankings:
            logger.warning("⚠️ [Scheduler] No NXT rankings data fetched.")
            return
            
        logger.info(f"✅ [Scheduler] Fetched {len(rankings)} NXT items.")
        
    except Exception as e:
        logger.error(f"❌ [Scheduler] Failed to fetch NXT data from KIS: {e}")
        return

    # 2. DB 저장 (market_type="NXT")
    async with AsyncSessionLocal() as session:
        try:
            today = datetime.now().date()
            await crud_daily_ranking.save_daily_rankings(session, today, rankings, market_type="NXT")
            logger.info(f"💾 [Scheduler] Successfully saved NXT rankings for {today}")
        except Exception as e:
            logger.error(f"❌ [Scheduler] Failed to save NXT data to DB: {e}")
            await session.rollback()


async def run_catchup_on_startup():
    """
    앱 시작 시 당일 누락 데이터 자동 보완
    재시작으로 인해 스케줄러가 15:40 / 20:00을 놓쳤을 경우 즉시 수집

    주의: 세션 중첩을 방지하기 위해 체크와 저장을 각각 독립된 세션으로 분리합니다.
    """
    now = datetime.now()

    if not is_market_open():
        logger.info("⛔ [Catchup] Today is holiday. Skip.")
        return

    today = now.date()

    # ── KRX: 15:40 이후인데 오늘 데이터가 없으면 즉시 수집 ──
    if now.hour > 15 or (now.hour == 15 and now.minute >= 40):
        # 세션 A: 존재 여부만 확인 후 즉시 닫음
        async with AsyncSessionLocal() as session:
            existing = await crud_daily_ranking.get_rankings_by_date(session, today, "KRX")

        if not existing:
            logger.info("🔄 [Catchup] KRX 데이터 누락. 즉시 보완 수집 시작...")
            await fetch_and_save_krx_rankings()  # 내부에서 독립된 세션 B로 저장
        else:
            logger.info(f"✅ [Catchup] KRX data exists for {today}. Skip.")

    # ── NXT: 20:00 이후인데 오늘 데이터가 없으면 즉시 수집 ──
    if now.hour >= 20:
        # 세션 C: 존재 여부만 확인 후 즉시 닫음
        async with AsyncSessionLocal() as session:
            existing = await crud_daily_ranking.get_rankings_by_date(session, today, "NXT")

        if not existing:
            logger.info("🔄 [Catchup] NXT 데이터 누락. 즉시 보완 수집 시작...")
            await fetch_and_save_nxt_rankings()  # 내부에서 독립된 세션 D로 저장
        else:
            logger.info(f"✅ [Catchup] NXT data exists for {today}. Skip.")

async def refresh_kis_token_job():
    """
    정기적인 KIS 액세스 토큰 갱신 작업
    매일 장 시작 전(07:50 등)에 강제로 새로운 토큰을 발급받아 캐시를 덮어씁니다.
    """
    logger.info("📅 [Scheduler] KIS Token Refresh Job Started")
    try:
        kis_client = await get_kis_client()
        # force=True를 통해 강제로 새 토큰 발급
        token = await kis_client.get_access_token(force=True)
        if token:
            logger.info("✅ [Scheduler] Successfully refreshed KIS access token. (force=True)")
        else:
            logger.warning("⚠️ [Scheduler] Token refresh returned empty string.")
    except Exception as e:
        logger.error(f"❌ [Scheduler] Failed to refresh KIS token: {e}")
