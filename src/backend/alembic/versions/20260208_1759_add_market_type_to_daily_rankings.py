"""Add market_type column to daily_rankings

Revision ID: a8f9c2b3d4e5
Revises: ce203b07ec81
Create Date: 2026-02-08 17:59:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8f9c2b3d4e5'
down_revision: Union[str, None] = 'ce203b07ec81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 기존 unique constraint 삭제
    op.drop_constraint('uq_daily_ranking_date_code', 'daily_rankings', type_='unique')
    
    # 2. 기존 인덱스 삭제
    op.drop_index('idx_trade_date_rank', table_name='daily_rankings')
    
    # 3. market_type 컬럼 추가 (기본값 KRX)
    op.add_column('daily_rankings', 
        sa.Column('market_type', sa.String(length=10), nullable=False, server_default='KRX', comment='시장구분 (KRX/NXT)')
    )
    
    # 4. 새로운 unique constraint 생성 (trade_date + stock_code + market_type)
    op.create_unique_constraint('uq_daily_ranking_date_code_market', 'daily_rankings', 
        ['trade_date', 'stock_code', 'market_type'])
    
    # 5. 새로운 인덱스 생성 (trade_date + market_type + rank)
    op.create_index('idx_trade_date_market_rank', 'daily_rankings', 
        ['trade_date', 'market_type', 'rank'], unique=False)


def downgrade() -> None:
    # 역순으로 복구
    op.drop_index('idx_trade_date_market_rank', table_name='daily_rankings')
    op.drop_constraint('uq_daily_ranking_date_code_market', 'daily_rankings', type_='unique')
    op.drop_column('daily_rankings', 'market_type')
    op.create_index('idx_trade_date_rank', 'daily_rankings', ['trade_date', 'rank'], unique=False)
    op.create_unique_constraint('uq_daily_ranking_date_code', 'daily_rankings', 
        ['trade_date', 'stock_code'])
