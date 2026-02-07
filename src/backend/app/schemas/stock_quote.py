from pydantic import BaseModel, Field
from datetime import datetime


class StockQuote(BaseModel):
    """실시간 주식 시세 정보"""
    stock_code: str = Field(..., description="종목코드 (6자리)")
    stock_name: str = Field("", description="종목명")
    current_price: int = Field(..., description="현재가")
    change_price: int = Field(..., description="전일대비 금액")
    change_rate: float = Field(..., description="등락률 (%)")
    opening_price: int = Field(..., description="시가")
    high_price: int = Field(..., description="고가")
    low_price: int = Field(..., description="저가")
    volume: int = Field(..., description="거래량")
    timestamp: datetime = Field(..., description="조회 시각")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "stock_code": "005930",
                "stock_name": "삼성전자",
                "current_price": 70000,
                "change_price": 1000,
                "change_rate": 1.45,
                "opening_price": 69500,
                "high_price": 70500,
                "low_price": 69000,
                "volume": 12345678,
                "timestamp": "2026-02-07T18:00:00"
            }
        }
