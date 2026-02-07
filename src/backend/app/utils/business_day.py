"""
영업일 판단 유틸리티
"""
from datetime import datetime, date, timedelta
import pytz

KST = pytz.timezone('Asia/Seoul')


def get_kst_now() -> datetime:
    """KST 기준 현재 시간"""
    return datetime.now(KST)


def is_business_day(dt: datetime = None) -> bool:
    """영업일 여부 확인 (주말 제외)
    
    Args:
        dt: 확인할 날짜/시간 (None이면 현재)
    
    Returns:
        bool: 영업일이면 True
    """
    if dt is None:
        dt = get_kst_now()
    
    # 주말 체크 (0=월요일, 6=일요일)
    if dt.weekday() >= 5:  # 5=토요일, 6=일요일
        return False
    
    # TODO: 공휴일 체크 (향후 확장)
    # 한국거래소 휴장일 API 또는 하드코딩된 공휴일 목록
    
    return True


def is_market_closed() -> bool:
    """장 마감 여부 확인 (15:30 이후)
    
    Returns:
        bool: 장 마감 시간(15:30) 이후면 True
    """
    now = get_kst_now()
    
    # 15:30 이후면 True
    if now.hour > 15:
        return True
    elif now.hour == 15 and now.minute >= 30:
        return True
    
    return False


def get_last_business_date(from_date: date = None) -> date:
    """마지막 영업일 날짜 조회
    
    Args:
        from_date: 기준 날짜 (None이면 오늘)
    
    Returns:
        date: 마지막 영업일 날짜
    """
    if from_date is None:
        from_date = get_kst_now().date()
    
    current = from_date
    
    # 최대 7일 전까지 검색 (주말 고려)
    for _ in range(7):
        # 해당 날짜의 datetime 생성
        dt = datetime.combine(current, datetime.min.time())
        dt = KST.localize(dt)
        
        if is_business_day(dt):
            return current
        
        current -= timedelta(days=1)
    
    # 폴백: 7일 내에 영업일이 없으면 오늘 반환
    return from_date


def get_today_kst() -> date:
    """KST 기준 오늘 날짜"""
    return get_kst_now().date()
