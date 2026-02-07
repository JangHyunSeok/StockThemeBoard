from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class ThemeStock(Base):
    """테마-종목 매핑 테이블 (중간 테이블)"""
    
    __tablename__ = "theme_stocks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    theme_id = Column(UUID(as_uuid=True), ForeignKey("themes.id", ondelete="CASCADE"), nullable=False)
    stock_code = Column(String(6), ForeignKey("stocks.code", ondelete="CASCADE"), nullable=False)
    weight = Column(Integer, default=5, nullable=False)  # 가중치 1-10 (기본값 5)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 관계
    theme = relationship("Theme", back_populates="theme_stocks")
    stock = relationship("Stock", back_populates="theme_stocks")
    
    # 제약조건: 동일한 테마-종목 조합 중복 방지
    __table_args__ = (
        UniqueConstraint("theme_id", "stock_code", name="uix_theme_stock"),
    )
    
    def __repr__(self):
        return f"<ThemeStock(theme_id={self.theme_id}, stock_code='{self.stock_code}', weight={self.weight})>"
