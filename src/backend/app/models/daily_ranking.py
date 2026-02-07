"""
일일 거래량 순위 모델
"""
from sqlalchemy import Column, Integer, String, Float, BigInteger, Date, DateTime, Index, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class DailyRanking(Base):
    """일일 거래량 순위"""
    __tablename__ = "daily_rankings"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_date = Column(Date, nullable=False, index=True, comment="거래일")
    stock_code = Column(String(10), nullable=False, comment="종목코드")
    stock_name = Column(String(100), nullable=False, comment="종목명")
    rank = Column(Integer, nullable=False, comment="순위")
    current_price = Column(Integer, nullable=False, comment="현재가")
    change_price = Column(Integer, nullable=False, comment="전일대비")
    change_rate = Column(Float, nullable=False, comment="등락률")
    volume = Column(BigInteger, nullable=False, comment="거래량")
    trading_value = Column(BigInteger, nullable=False, comment="거래대금")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="생성일시")
    
    # 복합 유니크 제약: 같은 날짜의 같은 종목은 중복 불가
    __table_args__ = (
        UniqueConstraint('trade_date', 'stock_code', name='uq_daily_ranking_date_code'),
        Index('idx_trade_date_rank', 'trade_date', 'rank'),  # 날짜+순위 인덱스
    )
    
    def __repr__(self):
        return f"<DailyRanking(date={self.trade_date}, rank={self.rank}, stock={self.stock_name})>"
