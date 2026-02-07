from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from typing import List, Optional


class StockInTheme(BaseModel):
    """테마 내 종목 정보 (간단 버전)"""
    code: str
    name: str
    market: str
    weight: int = Field(..., ge=1, le=10, description="종목 가중치 (1-10)")
    
    class Config:
        from_attributes = True


class ThemeBase(BaseModel):
    """Theme 기본 스키마"""
    name: str = Field(..., min_length=1, max_length=100, description="테마 이름")
    description: Optional[str] = Field(None, description="테마 설명")


class ThemeCreate(ThemeBase):
    """Theme 생성 요청 스키마"""
    pass


class ThemeResponse(ThemeBase):
    """Theme 응답 스키마"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ThemeWithStocks(ThemeResponse):
    """종목 목록을 포함한 Theme 응답 스키마"""
    stocks: List[StockInTheme] = []
    
    class Config:
        from_attributes = True
