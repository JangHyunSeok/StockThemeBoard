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
    market_type = Column(String(10), nullable=False, server_default='KRX', comment="시장구분 (KRX/NXT)")
    rank = Column(Integer, nullable=False, comment="순위")
    current_price = Column(Integer, nullable=False, comment="현재가")
    change_price = Column(Integer, nullable=False, comment="전일대비")
    change_rate = Column(Float, nullable=False, comment="등락률")
    volume = Column(BigInteger, nullable=False, comment="거래량")
    trading_value = Column(BigInteger, nullable=False, comment="거래대금")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="생성일시")
    
    # 복합 유니크 제약: 같은 날짜의 같은 종목이라도 시장구분이 다르면 허용 (KRX/NXT 별도 저장)
    __table_args__ = (
        UniqueConstraint('trade_date', 'stock_code', 'market_type', name='uq_daily_ranking_date_code_market'),
        Index('idx_trade_date_market_rank', 'trade_date', 'market_type', 'rank'),  # 날짜+시장+순위 인덱스
    )
    
    def __repr__(self):
        return f"<DailyRanking(date={self.trade_date}, rank={self.rank}, stock={self.stock_name})>"
