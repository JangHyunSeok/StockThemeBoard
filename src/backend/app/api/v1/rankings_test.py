"""
테스트용 간단한 API - 실제 KIS API 없이도 동작
"""
from fastapi import APIRouter
from typing import Dict, List
import random

router = APIRouter()

# 테스트용 더미 데이터
DUMMY_STOCKS = [
    {"name": "삼성전자", "code": "005930"},
    {"name": "SK하이닉스", "code": "000660"},
    {"name": "LG에너지솔루션", "code": "373220"},
    {"name": "삼성바이오로직스", "code": "207940"},
    {"name": "현대차", "code": "005380"},
    {"name": "POSCO홀딩스", "code": "005490"},
    {"name": "네이버", "code": "035420"},
    {"name": "카카오", "code": "035720"},
    {"name": "LG화학", "code": "051910"},
    {"name": "기아", "code": "000270"},
]

THEME_KEYWORDS = {
    "인공지능(AI)": ["삼성전자", "SK하이닉스", "네이버", "카카오"],
    "반도체": ["삼성전자", "SK하이닉스"],
    "2차전지": ["LG에너지솔루션", "LG화학"],
    "바이오/헬스케어": ["삼성바이오로직스"],
    "전기차": ["현대차", "기아"],
    "2차전지 소재": ["LG화학", "POSCO홀딩스"],
}


@router.get("/volume-rank-by-theme-test")
async def get_volume_rank_by_theme_test():
    """테스트용 거래량 순위 API (더미 데이터)"""
    
    result = {}
    
    for theme_name, keywords in THEME_KEYWORDS.items():
        theme_stocks = []
        for i, keyword in enumerate(keywords[:4], 1):  # 최대 4개
            # 해당 키워드를 포함하는 종목 찾기
            stock = next((s for s in DUMMY_STOCKS if keyword in s["name"]), None)
            if stock:
                theme_stocks.append({
                    "code": stock["code"],
                    "name": stock["name"],
                    "rank": i,
                    "current_price": random.randint(50000, 100000),
                    "change_price": random.randint(-5000, 5000),
                    "change_rate": round(random.uniform(-5.0, 5.0), 2),
                    "volume": random.randint(1000000, 10000000),
                    "trading_value": random.randint(1000000000, 100000000000),
                })
        
        result[theme_name] = theme_stocks
    
    return result
