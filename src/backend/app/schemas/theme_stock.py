from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class ThemeStockCreate(BaseModel):
    """테마에 종목 추가 요청"""
    stock_code: str = Field(..., min_length=6, max_length=6, description="종목코드 (6자리)")
    weight: int = Field(5, ge=1, le=10, description="종목 가중치 (1-10, 기본값 5)")


class ThemeStockUpdate(BaseModel):
    """종목 가중치 수정 요청"""
    weight: int = Field(..., ge=1, le=10, description="종목 가중치 (1-10)")


class ThemeStockResponse(BaseModel):
    """ThemeStock 응답 스키마"""
    id: UUID
    theme_id: UUID
    stock_code: str
    weight: int
    created_at: datetime
    
    class Config:
        from_attributes = True
