from pydantic import BaseModel
from datetime import datetime
from typing import List

class IndexQuote(BaseModel):
    index_code: str
    current_price: float
    change_price: float
    change_rate: float
    timestamp: datetime

class IndicesResponse(BaseModel):
    items: List[IndexQuote]
