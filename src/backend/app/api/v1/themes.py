from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.database import get_db
from app.crud import theme as crud_theme, stock as crud_stock, theme_stock as crud_theme_stock
from app.schemas.theme import ThemeCreate, ThemeResponse, ThemeWithStocks
from app.schemas.theme_stock import ThemeStockCreate, ThemeStockUpdate, ThemeStockResponse

router = APIRouter()


@router.get("", response_model=List[ThemeResponse], summary="테마 목록 조회")
async def get_themes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    테마 목록을 조회합니다.
    
    - **skip**: 건너뛸 항목 수 (페이지네이션)
    - **limit**: 반환할 최대 항목 수 (기본: 100)
    """
    themes = await crud_theme.get_themes(db, skip=skip, limit=limit)
    return themes


@router.get("/{theme_id}", response_model=ThemeWithStocks, summary="테마 상세 조회")
async def get_theme(
    theme_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    특정 테마의 상세 정보를 조회합니다. (포함: 관련 종목 목록)
    
    - **theme_id**: 조회할 테마의 UUID
    """
    theme = await crud_theme.get_theme_by_id(db, theme_id=theme_id)
    if theme is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Theme with id {theme_id} not found"
        )
    return theme


@router.post("", response_model=ThemeResponse, status_code=status.HTTP_201_CREATED, summary="테마 생성")
async def create_theme(
    theme: ThemeCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    새로운 테마를 생성합니다.
    
    - **name**: 테마 이름 (필수, 중복 불가)
    - **description**: 테마 설명 (선택)
    """
    # 중복 체크
    existing_theme = await crud_theme.get_theme_by_name(db, name=theme.name)
    if existing_theme:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Theme with name '{theme.name}' already exists"
        )
    
    return await crud_theme.create_theme(db, theme=theme)


# === 테마-종목 관계 관리 API ===

@router.post(
    "/{theme_id}/stocks",
    response_model=ThemeStockResponse,
    status_code=status.HTTP_201_CREATED,
    summary="테마에 종목 추가"
)
async def add_stock_to_theme(
    theme_id: UUID,
    theme_stock: ThemeStockCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    테마에 종목을 추가합니다.
    
    - **theme_id**: 테마 UUID
    - **stock_code**: 추가할 종목코드 (6자리)
    - **weight**: 종목 가중치 (1-10, 기본값 5)
    """
    # 테마 존재 확인
    theme = await crud_theme.get_theme_by_id(db, theme_id=theme_id)
    if theme is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Theme with id {theme_id} not found"
        )
    
    # 종목 존재 확인
    stock = await crud_stock.get_stock_by_code(db, code=theme_stock.stock_code)
    if stock is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock with code {theme_stock.stock_code} not found"
        )
    
    # 중복 체크
    existing = await crud_theme_stock.get_theme_stock(
        db, theme_id=theme_id, stock_code=theme_stock.stock_code
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock {theme_stock.stock_code} is already in theme {theme_id}"
        )
    
    # 종목 추가
    return await crud_theme_stock.add_stock_to_theme(
        db,
        theme_id=theme_id,
        stock_code=theme_stock.stock_code,
        weight=theme_stock.weight
    )


@router.put(
    "/{theme_id}/stocks/{stock_code}",
    response_model=ThemeStockResponse,
    summary="종목 가중치 수정"
)
async def update_stock_weight(
    theme_id: UUID,
    stock_code: str,
    update_data: ThemeStockUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    테마 내 종목의 가중치를 수정합니다.
    
    - **theme_id**: 테마 UUID
    - **stock_code**: 종목코드 (6자리)
    - **weight**: 새로운 가중치 (1-10)
    """
    # 관계 존재 확인
    theme_stock = await crud_theme_stock.get_theme_stock(
        db, theme_id=theme_id, stock_code=stock_code
    )
    if theme_stock is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock {stock_code} not found in theme {theme_id}"
        )
    
    # 가중치 수정
    updated = await crud_theme_stock.update_stock_weight(
        db,
        theme_id=theme_id,
        stock_code=stock_code,
        weight=update_data.weight
    )
    return updated


@router.delete(
    "/{theme_id}/stocks/{stock_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="테마에서 종목 제거"
)
async def remove_stock_from_theme(
    theme_id: UUID,
    stock_code: str,
    db: AsyncSession = Depends(get_db)
):
    """
    테마에서 종목을 제거합니다.
    
    - **theme_id**: 테마 UUID
    - **stock_code**: 제거할 종목코드 (6자리)
    """
    # 관계 존재 확인
    theme_stock = await crud_theme_stock.get_theme_stock(
        db, theme_id=theme_id, stock_code=stock_code
    )
    if theme_stock is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock {stock_code} not found in theme {theme_id}"
        )
    
    # 종목 제거
    await crud_theme_stock.remove_stock_from_theme(
        db, theme_id=theme_id, stock_code=stock_code
    )
    return None

