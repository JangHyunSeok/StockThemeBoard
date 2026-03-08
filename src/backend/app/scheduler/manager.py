
"""
APScheduler 관리 모듈
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from app.scheduler.jobs import fetch_and_save_krx_rankings, fetch_and_save_nxt_rankings, refresh_kis_token_job

logger = logging.getLogger(__name__)

# 스케줄러 인스턴스 (싱글톤)
scheduler = AsyncIOScheduler()

def start_scheduler():
    """스케줄러 시작 및 Job 등록"""
    if scheduler.running:
        return

    # TZ: Asia/Seoul
    seoul_tz = timezone('Asia/Seoul')

    # Job 1: KRX 정규장 종가 - 평일(월~금) 15시 40분
    krx_trigger = CronTrigger(
        day_of_week='mon-fri',
        hour=15,
        minute=40,
        timezone=seoul_tz
    )
    
    scheduler.add_job(
        fetch_and_save_krx_rankings,
        trigger=krx_trigger,
        id="krx_daily_ranking_job",
        replace_existing=True,
        misfire_grace_time=3600  # 재시작으로 놓쳤을 때 1시간 이내면 즉시 실행
    )
    
    # Job 2: NXT 야간거래 종가 - 평일(월~금) 20시 00분
    nxt_trigger = CronTrigger(
        day_of_week='mon-fri',
        hour=20,
        minute=0,
        timezone=seoul_tz
    )
    
    scheduler.add_job(
        fetch_and_save_nxt_rankings,
        trigger=nxt_trigger,
        id="nxt_daily_ranking_job",
        replace_existing=True,
        misfire_grace_time=3600  # 재시작으로 놓쳤을 때 1시간 이내면 즉시 실행
    )
    
    # Job 3: KIS API 토큰 사전 발급 (Pre-warming) - 평일(월~금) 07시 50분
    token_trigger = CronTrigger(
        day_of_week='mon-fri',
        hour=7,
        minute=50,
        timezone=seoul_tz
    )
    
    scheduler.add_job(
        refresh_kis_token_job,
        trigger=token_trigger,
        id="refresh_kis_token_job",
        replace_existing=True,
        misfire_grace_time=3600
    )
    
    scheduler.start()
    logger.info("⏰ [Scheduler] Started.")
    logger.info("  - KIS Token Refresh Job at 07:50 (Mon-Fri)")
    logger.info("  - KRX Job at 15:40 (Mon-Fri)")
    logger.info("  - NXT Job at 20:00 (Mon-Fri)")

def shutdown_scheduler():
    """스케줄러 종료"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("💤 [Scheduler] Shutdown.")
