from fastapi import APIRouter, HTTPException, status
from typing import List, Dict

from app.services.kis_client import get_kis_client
from app.services.redis_client import get_cache, set_cache
from app.schemas.stock_ranking import StockRanking
import json


router = APIRouter()


# 테마별 키워드 매핑
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


@router.get("/volume-rank-by-theme")
async def get_volume_rank_by_theme():
    """테마별 거래량 상위 종목 조회
    
    각 테마별로 거래량 상위 종목을 최대 15개씩 반환
    """
    # 캐시 확인
    cache_key = "volume_rank_by_theme"
    cached_data = await get_cache(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    try:
        # KIS API에서 거래량 상위 100개 조회
        kis_client = await get_kis_client()
        rankings = await kis_client.get_volume_rank(limit=100)
        
        # 테마별로 분류
        theme_stocks: Dict[str, List[StockRanking]] = {
            theme: [] for theme in THEME_KEYWORDS.keys()
        }
        
        for stock_data in rankings:
            stock_name = stock_data["name"]
            matched_themes = match_theme(stock_name)
            
            for theme_name in matched_themes:
                if len(theme_stocks[theme_name]) < 15:  # 테마당 최대 15개
                    theme_stocks[theme_name].append(StockRanking(**stock_data))
        
        # 딕셔너리로 변환
        result = {}
        for theme_name, stocks in theme_stocks.items():
            result[theme_name] = [stock.model_dump() for stock in stocks]
        
        # 캐시 저장 (60초)
        await set_cache(cache_key, json.dumps(result, ensure_ascii=False), ttl=60)
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"거래량 순위 조회 실패: {str(e)}"
        )
