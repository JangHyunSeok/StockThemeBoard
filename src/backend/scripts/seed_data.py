"""
초기 데이터 생성 스크립트

주요 테마와 대표 종목을 데이터베이스에 추가합니다.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.theme import Theme
from app.models.stock import Stock
from app.models.theme_stock import ThemeStock


# 비동기 세션 생성
engine = create_async_engine(settings.DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# 테마 데이터
THEMES = [
    {
        "name": "인공지능(AI)",
        "description": "AI 반도체, 데이터센터, 생성형 AI 관련주"
    },
    {
        "name": "반도체",
        "description": "메모리 반도체, 시스템 반도체, 반도체 장비"
    },
    {
        "name": "2차전지",
        "description": "배터리, 양극재, 음극재, 전해액, 분리막"
    },
    {
        "name": "바이오/헬스케어",
        "description": "제약, 바이오 신약, 의료기기"
    },
    {
        "name": "전기차",
        "description": "전기차, 자율주행, 모빌리티"
    },
    {
        "name": "2차전지 소재",
        "description": "양극재, 음극재, 전해액, 분리막 등 배터리 핵심 소재"
    }
]


# 종목 데이터 (주요 대형주 + 테마주)
STOCKS = [
    # 반도체 & AI
    {"code": "005930", "name": "삼성전자", "market": "KOSPI", "market_cap": 400000000000000},
    {"code": "000660", "name": "SK하이닉스", "market": "KOSPI", "market_cap": 120000000000000},
    
    # 2차전지
    {"code": "373220", "name": "LG에너지솔루션", "market": "KOSPI", "market_cap": 100000000000000},
    {"code": "247540", "name": "에코프로비엠", "market": "KOSDAQ", "market_cap": 15000000000000},
    {"code": "086520", "name": "에코프로", "market": "KOSPI", "market_cap": 12000000000000},
    
    # 화학 (2차전지 소재)
    {"code": "051910", "name": "LG화학", "market": "KOSPI", "market_cap": 50000000000000},
    {"code": "096770", "name": "SK이노베이션", "market": "KOSPI", "market_cap": 25000000000000},
    
    # 전기차
    {"code": "005380", "name": "현대차", "market": "KOSPI", "market_cap": 80000000000000},
    {"code": "000270", "name": "기아", "market": "KOSPI", "market_cap": 60000000000000},
    
    # 바이오
    {"code": "207940", "name": "삼성바이오로직스", "market": "KOSPI", "market_cap": 70000000000000},
    {"code": "068270", "name": "셀트리온", "market": "KOSPI", "market_cap": 35000000000000},
    {"code": "326030", "name": "SK바이오팜", "market": "KOSPI", "market_cap": 8000000000000},
]


# 테마-종목 매핑
THEME_STOCK_MAPPINGS = [
    # 인공지능(AI)
    ("인공지능(AI)", "005930", 10),  # 삼성전자
    ("인공지능(AI)", "000660", 9),   # SK하이닉스
    
    # 반도체
    ("반도체", "005930", 10),  # 삼성전자
    ("반도체", "000660", 10),  # SK하이닉스
    
    # 2차전지
    ("2차전지", "373220", 10),  # LG에너지솔루션
    ("2차전지", "247540", 9),   # 에코프로비엠
    ("2차전지", "086520", 8),   # 에코프로
    ("2차전지", "051910", 7),   # LG화학
    ("2차전지", "096770", 6),   # SK이노베이션
    
    # 2차전지 소재
    ("2차전지 소재", "247540", 10),  # 에코프로비엠
    ("2차전지 소재", "086520", 9),   # 에코프로
    ("2차전지 소재", "051910", 8),   # LG화학
    
    # 전기차
    ("전기차", "005380", 10),  # 현대차
    ("전기차", "000270", 9),   # 기아
    ("전기차", "373220", 8),   # LG에너지솔루션
    
    # 바이오/헬스케어
    ("바이오/헬스케어", "207940", 10),  # 삼성바이오로직스
    ("바이오/헬스케어", "068270", 9),   # 셀트리온
    ("바이오/헬스케어", "326030", 8),   # SK바이오팜
]


async def seed_data():
    """초기 데이터 생성"""
    async with async_session() as session:
        print("🌱 데이터베이스 초기화 시작...\n")
        
        # 1. 테마 생성
        print("📋 테마 생성 중...")
        theme_dict = {}
        for theme_data in THEMES:
            theme = Theme(**theme_data)
            session.add(theme)
            await session.flush()  # ID 생성을 위해 flush
            theme_dict[theme_data["name"]] = theme
            print(f"  ✅ {theme.name}")
        
        await session.commit()
        print(f"\n총 {len(THEMES)}개 테마 생성 완료!\n")
        
        # 2. 종목 생성
        print("📈 종목 등록 중...")
        stock_dict = {}
        for stock_data in STOCKS:
            stock = Stock(**stock_data)
            session.add(stock)
            stock_dict[stock_data["code"]] = stock
            print(f"  ✅ {stock.name} ({stock.code})")
        
        await session.commit()
        print(f"\n총 {len(STOCKS)}개 종목 등록 완료!\n")
        
        # 3. 테마-종목 매핑
        print("🔗 테마-종목 매핑 중...")
        for theme_name, stock_code, weight in THEME_STOCK_MAPPINGS:
            theme = theme_dict[theme_name]
            theme_stock = ThemeStock(
                theme_id=theme.id,
                stock_code=stock_code,
                weight=weight
            )
            session.add(theme_stock)
            stock_name = stock_dict[stock_code].name
            print(f"  ✅ {theme_name} ← {stock_name} (가중치: {weight})")
        
        await session.commit()
        print(f"\n총 {len(THEME_STOCK_MAPPINGS)}개 매핑 완료!\n")
        
        print("=" * 60)
        print("🎉 초기 데이터 생성 완료!")
        print("=" * 60)
        print(f"\n📊 생성된 데이터:")
        print(f"  - 테마: {len(THEMES)}개")
        print(f"  - 종목: {len(STOCKS)}개")
        print(f"  - 매핑: {len(THEME_STOCK_MAPPINGS)}개")
        print("\n✨ 이제 API를 통해 데이터를 조회할 수 있습니다!")
        print("   👉 http://localhost:8000/docs\n")


async def main():
    """메인 함수"""
    try:
        await seed_data()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
