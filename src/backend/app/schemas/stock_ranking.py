from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class StockRanking(BaseModel):
    """거래량 순위 종목 정보"""
    code: str = Field(..., description="종목코드")
    name: str = Field(..., description="종목명")
    rank: int = Field(..., description="순위")
    current_price: int = Field(..., description="현재가")
    change_price: int = Field(..., description="전일대비")
    change_rate: float = Field(..., description="등락률 (%)")
    volume: int = Field(..., description="거래량")
    trading_value: int = Field(..., description="거래대금")
    
    class Config:
        from_attributes = True
