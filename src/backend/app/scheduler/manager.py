
"""
APScheduler 관리 모듈
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from app.scheduler.jobs import fetch_and_save_daily_rankings

logger = logging.getLogger(__name__)

# 스케줄러 인스턴스 (싱글톤)
scheduler = AsyncIOScheduler()

def start_scheduler():
    """스케줄러 시작 및 Job 등록"""
    if scheduler.running:
        return

    # TZ: Asia/Seoul
    seoul_tz = timezone('Asia/Seoul')

    # Job: 평일(월~금) 15시 40분에 실행
    trigger = CronTrigger(
        day_of_week='mon-fri',
        hour=15,
        minute=40,
        timezone=seoul_tz
    )
    
    scheduler.add_job(
        fetch_and_save_daily_rankings,
        trigger=trigger,
        id="daily_ranking_job",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("⏰ [Scheduler] Started. Job 'daily_ranking_job' scheduled at 15:40 (Mon-Fri).")

def shutdown_scheduler():
    """스케줄러 종료"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("zzz [Scheduler] Shutdown.")
