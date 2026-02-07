from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class StockBase(BaseModel):
    """Stock 기본 스키마"""
    code: str = Field(..., min_length=6, max_length=6, description="종목코드 (6자리)")
    name: str = Field(..., min_length=1, max_length=100, description="종목명")
    market: str = Field(..., description="시장 (KOSPI/KOSDAQ)")
    market_cap: Optional[int] = Field(None, ge=0, description="시가총액 (원)")


class StockCreate(StockBase):
    """Stock 생성 요청 스키마"""
    pass


class StockResponse(StockBase):
    """Stock 응답 스키마"""
    created_at: datetime
    
    class Config:
        from_attributes = True
