
"""
공통 유틸리티 함수
"""
from datetime import datetime, date
import holidays

# 한국 공휴일 (관공서 공휴일 기준)
kr_holidays = holidays.KR()

def is_market_open(target_date: date = None) -> bool:
    """
    해당 날짜가 주식 시장이 열리는 날인지 확인
    (주말 및 공휴일 제외)
    
    Args:
        target_date: 확인할 날짜 (기본값: 오늘)
    
    Returns:
        bool: 개장일이면 True, 휴장일이면 False
    """
    if target_date is None:
        target_date = datetime.now().date()
    
    # 1. 주말 체크 (5:토, 6:일)
    if target_date.weekday() >= 5:
        return False
    
    # 2. 공휴일 체크
    if target_date in kr_holidays:
        return False
        
    return True

def get_last_market_date() -> date:
    """
    가장 최근 개장일 조회
    (오늘이 개장일이면 오늘 리턴, 휴장이면 직전 평일 리턴)
    """
    from datetime import timedelta
    
    current_date = datetime.now().date()
    # 최근 10일 전까지 검색 (설날/추석 연휴 고려)
    for _ in range(10):
        if is_market_open(current_date):
            return current_date
        current_date -= timedelta(days=1)
        
    return current_date  # Fallback


def get_current_market_type() -> str:
    """현재 시간대에 맞는 시장 타입 반환
    
    Returns:
        "KRX" (한국거래소: 09:00~20:00) or "NXT" (대체거래소: 20:00~09:00)
    """
    now = datetime.now()
    
    # 20:00 ~ 09:00 사이는 대체거래소(NXT) 시간대
    if now.hour >= 20 or now.hour < 9:
        return "NXT"
    
    # 휴장일(주말/공휴일)인 경우 기본적으로 대체거래소 데이터 우선 표시
    if not is_market_open():
        return "NXT"
    
    return "KRX"
