from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.crud import stock as crud_stock
from app.schemas.stock import StockCreate, StockResponse

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
