from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Theme(Base):
    """테마 모델"""
    
    __tablename__ = "themes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 관계 (many-to-many through ThemeStock)
    theme_stocks = relationship("ThemeStock", back_populates="theme", cascade="all, delete-orphan")
    
    @property
    def stocks(self):
        """테마의 종목 목록 반환 (가중치 포함)"""
        from app.schemas.theme import StockInTheme
        result = []
        for ts in self.theme_stocks:
            if ts.stock:
                result.append(StockInTheme(
                    code=ts.stock.code,
                    name=ts.stock.name,
                    market=ts.stock.market,
                    weight=ts.weight
                ))
        return result
    
    def __repr__(self):
        return f"<Theme(id={self.id}, name='{self.name}')>"
