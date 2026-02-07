from sqlalchemy import Column, String, BigInteger, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Stock(Base):
    """종목 모델"""
    
    __tablename__ = "stocks"
    
    code = Column(String(6), primary_key=True)  # 종목코드 (6자리)
    name = Column(String(100), nullable=False, index=True)
    market = Column(String(50), nullable=False)  # KOSPI, KOSDAQ
    market_cap = Column(BigInteger)  # 시가총액 (원 단위)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 관계 (many-to-many through ThemeStock)
    theme_stocks = relationship("ThemeStock", back_populates="stock", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Stock(code='{self.code}', name='{self.name}')>"
