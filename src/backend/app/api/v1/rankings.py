from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict
from collections import OrderedDict
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date, timedelta
import asyncio
import json

from app.services.kis_client import get_kis_client
from app.services.redis_client import get_cache, set_cache
from app.schemas.stock_ranking import StockRanking
from app.crud import daily_ranking as crud_daily_ranking
from app.database import get_db
import json


router = APIRouter()


def is_weekend() -> bool:
    """주말 여부 확인 (간단 버전)"""
    today = datetime.now()
    return today.weekday() >= 5  # 5=토요일, 6=일요일


def is_after_market_close() -> bool:
    """장 마감 시간(15:30) 이후 확인"""
    now = datetime.now()
    return now.hour > 15 or (now.hour == 15 and now.minute >= 30)


def get_last_weekday() -> date:
    """마지막 평일 날짜 조회"""
    today = datetime.now().date()
    current = today
    
    # 최대 7일 전까지 검색
    for _ in range(7):
        dt = datetime.combine(current, datetime.min.time())
        if dt.weekday() < 5:  # 평일
            return current
        current -= timedelta(days=1)
    
    return today


# 테마별 키워드 매핑 (분류용)
THEME_KEYWORDS = {
    "인공지능(AI)": ["AI", "인공지능", "NVIDIA", "삼성전자", "SK하이닉스", "네이버", "카카오"],
    "반도체": ["반도체", "삼성전자", "SK하이닉스", "DB하이텍", "SK스퀘어"],
    "2차전지": ["배터리", "LG에너지솔루션", "에코프로", "포스코퓨처엠", "삼성SDI"],
    "바이오/헬스케어": ["바이오", "제약", "셀트리온", "삼성바이오로직스", "SK바이오팜"],
    "전기차": ["전기차", "현대차", "기아", "현대모비스", "LG전자"],
    "2차전지 소재": ["에코프로", "포스코퓨처엠", "LG화학", "SK", "엘앤에프"],
}


def match_theme(stock_name: str) -> List[str]:
    """종목명으로 테마 매칭"""
    matched_themes = []
    for theme_name, keywords in THEME_KEYWORDS.items():
        for keyword in keywords:
            if keyword in stock_name:
                matched_themes.append(theme_name)
                break
    return matched_themes


def classify_and_sort_by_theme(rankings: List[Dict]) -> Dict[str, List[Dict]]:
    """테마별 분류 및 거래대금 순 정렬"""
    theme_stocks: Dict[str, List[Dict]] = {}
    
    for stock_data in rankings:
        stock_name = stock_data["name"]
        matched_themes = match_theme(stock_name)
        
        for theme_name in matched_themes:
            if theme_name not in theme_stocks:
                theme_stocks[theme_name] = []
            
            if len(theme_stocks[theme_name]) < 15:
                theme_stocks[theme_name].append(stock_data)
    
    # 각 테마의 총 거래대금 계산
    theme_totals = {}
    for theme_name, stocks in theme_stocks.items():
        total_trading_value = sum(stock["trading_value"] for stock in stocks)
        theme_totals[theme_name] = total_trading_value
    
    # 테마를 총 거래대금 순으로 정렬
    sorted_themes = sorted(
        theme_totals.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # 정렬된 순서로 결과 생성
    result = OrderedDict()
    for theme_name, _ in sorted_themes:
        stocks = theme_stocks[theme_name]
        result[theme_name] = [StockRanking(**stock).model_dump() for stock in stocks]
    
    return result


from app.core.utils import is_market_open, get_last_market_date

# ... (기존 코드 유지) ...

@router.get("/volume-rank-by-theme")
async def get_volume_rank_by_theme(db: AsyncSession = Depends(get_db)):
    """테마별 거래량 상위 종목 조회 (영업일/휴일 대응)"""
    cache_key = "volume_rank_by_theme"
    cached_data = await get_cache(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    try:
        rankings = []
        
        # 개장일 여부 확인 (주말 + 공휴일 체크)
        market_open = is_market_open()
        
        if market_open:
            # 개장일: KIS API 조회
            kis_client = await get_kis_client()
            rankings = await kis_client.get_volume_rank(limit=100)
            
            # 15:30 이후면 DB에 저장
            if is_after_market_close():
                today = datetime.now().date()
                await crud_daily_ranking.save_daily_rankings(db, today, rankings)
        else:
            # 휴장일: 가장 최근 개장일 DB 조회
            last_market_date = get_last_market_date()
            rankings = await crud_daily_ranking.get_rankings_by_date(db, last_market_date)
            
            if not rankings:
                rankings = []
            
            # 실시간 시세 업데이트 (병렬 처리)
            if rankings:
                try:
                    kis_client = await get_kis_client()
                    
                    # 1. 토큰 미리 확보 (Concurrency Issue 방지)
                    await kis_client.get_access_token()
                    
                    # 2. 업데이트 함수 정의
                    async def update_quote(ranking):
                        try:
                            # DB의 종목 코드로 실시간 시세 조회
                            quote = await kis_client.get_stock_quote(ranking['code'])
                            
                            # 순위는 유지하되, 가격/거래량 정보는 실시간 데이터로 덮어쓰기
                            ranking['current_price'] = quote['current_price']
                            ranking['change_price'] = quote['change_price']
                            ranking['change_rate'] = quote['change_rate']
                            ranking['volume'] = quote['volume']
                            ranking['trading_value'] = quote.get('trading_value', 0)
                            
                        except Exception as e:
                            # 개별 종목 조회 실패 시 로그만 남기고 기존 DB 데이터 유지
                            print(f"[Warn] 실시간 시세 조회 실패 ({ranking.get('name', '')}): {str(e)}")

                    # 3. 청크 단위 병렬 실행 (Rate Limit 고려)
                    # 실전투자: 초당 20건 제한 / 모의투자: 초당 2건 제한
                    # 성능 개선을 위해 20개씩 병렬 호출하되, 텀을 아주 짧게 둡니다.
                    CHUNK_SIZE = 20
                    for i in range(0, len(rankings), CHUNK_SIZE):
                        chunk = rankings[i:i + CHUNK_SIZE]
                        await asyncio.gather(*[update_quote(r) for r in chunk])
                        # API 과부하 방지를 위한 짧은 대기 (0.05초)
                        await asyncio.sleep(0.05)
                        
                except Exception as e:
                    print(f"[Error] 실시간 시세 업데이트 프로세스 실패: {str(e)}")
                    # 전체 프로세스 실패 시에도 DB에 있는 기존 데이터는 반환
        
        # 테마별 분류 및 정렬
        result = classify_and_sort_by_theme(rankings)
        
        # 캐시 저장 (5초 - 실시간성 우선)
        await set_cache(cache_key, json.dumps(result, ensure_ascii=False), ttl=5)
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"거래량 순위 조회 실패: {str(e)}"
        )
