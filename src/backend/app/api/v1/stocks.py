from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json

from app.database import get_db
from app.crud import stock as crud_stock
from app.schemas.stock import StockCreate, StockResponse
from app.schemas.stock_quote import StockQuote
from app.services.kis_client import get_kis_client
from app.services.redis_client import get_cache, set_cache

router = APIRouter()


@router.get("", response_model=List[StockResponse], summary="종목 목록 조회")
async def get_stocks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    종목 목록을 조회합니다.
    
    - **skip**: 건너뛸 항목 수 (페이지네이션)
    - **limit**: 반환할 최대 항목 수 (기본: 100)
    """
    stocks = await crud_stock.get_stocks(db, skip=skip, limit=limit)
    return stocks


@router.get("/{code}", response_model=StockResponse, summary="종목 상세 조회")
async def get_stock(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    """
    특정 종목의 상세 정보를 조회합니다.
    
    - **code**: 조회할 종목코드 (6자리)
    """
    stock = await crud_stock.get_stock_by_code(db, code=code)
    if stock is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock with code {code} not found"
        )
    return stock


@router.post("", response_model=StockResponse, status_code=status.HTTP_201_CREATED, summary="종목 생성")
async def create_stock(
    stock: StockCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    새로운 종목을 생성합니다.
    
    - **code**: 종목코드 (6자리, 필수, 중복 불가)
    - **name**: 종목명 (필수)
    - **market**: 시장 (KOSPI/KOSDAQ, 필수)
    - **market_cap**: 시가총액 (선택)
    """
    # 중복 체크
    existing_stock = await crud_stock.get_stock_by_code(db, code=stock.code)
    if existing_stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock with code '{stock.code}' already exists"
        )
    
    return await crud_stock.create_stock(db, stock=stock)


# === 실시간 시세 조회 API ===

@router.get("/{code}/quote", response_model=StockQuote, summary="실시간 시세 조회")
async def get_stock_quote(code: str, db: AsyncSession = Depends(get_db)):
    """
    한국투자증권 API를 통해 실시간 주식 시세를 조회합니다.
    
    - **code**: 종목코드 (6자리)
    
    캐싱: 60초간 Redis에 캐시됨
    """
    # 종목코드 유효성 검사
    if len(code) != 6 or not code.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="종목코드는 6자리 숫자여야 합니다"
        )
    
    # Redis 캐시 확인
    cache_key = f"quote:{code}"
    cached_data = await get_cache(cache_key)
    
    if cached_data:
        # 캐시된 데이터 반환
        quote_dict = json.loads(cached_data)
        return StockQuote(**quote_dict)
    
    # KIS API 클라이언트에서 시세 조회
    try:
        kis_client = await get_kis_client()
        quote_data = await kis_client.get_stock_quote(code)
        
        # DB에서 종목명 조회
        stock = await crud_stock.get_stock_by_code(db, code=code)
        if stock:
            quote_data["stock_name"] = stock.name
        else:
            quote_data["stock_name"] = f"종목({code})"  # DB에 없으면 기본값
        
        # StockQuote 객체 생성
        quote = StockQuote(**quote_data)
        
        # Redis에 캐시 (60초)
        await set_cache(cache_key, quote.model_dump_json(), ttl=60)
        
        return quote
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"시세 조회 실패: {str(e)}"
        )
